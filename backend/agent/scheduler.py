import threading
import time
from datetime import datetime, timedelta
from backend.db.database import SessionLocal, Base, engine
from backend.db.models import AutoScheduleConfig, BacklinkSubmission
from backend.agent.backlink_engine import run_auto_backlink_campaign

_scheduler_thread = None

def check_and_run_daily_schedule():
    db = SessionLocal()
    try:
        config = db.query(AutoScheduleConfig).first()
        if not config:
            config = AutoScheduleConfig(
                target_url="https://fairepairs.com/",
                target_keyword="SEO optimization guide",
                daily_goal=300,
                is_enabled=1,
                last_run_at=None,
                next_run_at=datetime.utcnow()
            )
            db.add(config)
            db.commit()
            db.refresh(config)

        if config.is_enabled == 1:
            now = datetime.utcnow()
            due_for_run = False

            if not config.last_run_at:
                due_for_run = True
            elif (now - config.last_run_at).total_seconds() >= 86400: # 24 hours = 86400s
                due_for_run = True

            if due_for_run:
                print(f"[24/7 Agentic Auto-Scheduler] Starting daily automated campaign for {config.target_url} ({config.daily_goal} links)...")
                res = run_auto_backlink_campaign(
                    target_url=config.target_url,
                    target_keyword=config.target_keyword,
                    count=config.daily_goal,
                    db=db
                )
                config.last_run_at = now
                config.next_run_at = now + timedelta(days=1)
                config.updated_at = now
                db.commit()
                print(f"[24/7 Agentic Auto-Scheduler] Successfully created {res.get('total_created', 0)} daily backlinks!")
    except Exception as e:
        print(f"[24/7 Agentic Auto-Scheduler] Error during schedule check: {e}")
    finally:
        db.close()

def scheduler_loop():
    print("[24/7 Agentic Auto-Scheduler] Background daemon active and monitoring daily schedule.")
    while True:
        try:
            check_and_run_daily_schedule()
        except Exception as e:
            print(f"Scheduler loop error: {e}")
        time.sleep(60) # Check every 60 seconds

def start_background_scheduler():
    global _scheduler_thread
    if _scheduler_thread is None or not _scheduler_thread.is_alive():
        _scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
        _scheduler_thread.start()
