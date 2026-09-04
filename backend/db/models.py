from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, Text
from datetime import datetime
from backend.db.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    target = Column(String, index=True) # URL or local file path
    target_type = Column(String, default="url") # "url" or "file"
    target_keyword = Column(String, nullable=True)
    page_type = Column(String, default="general") # "blog", "product", "homepage", etc.
    overall_score = Column(Float, default=0.0)
    category_scores = Column(JSON, default={}) # e.g., {"title": 80, "technical": 100}
    checks_result = Column(JSON, default=[]) # list of check results (pass, warn, fail, fix)
    planner_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class KeywordCache(Base):
    __tablename__ = "keyword_cache"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String, unique=True, index=True)
    trends_data = Column(JSON, default={})
    suggestions = Column(JSON, default=[])
    paa_questions = Column(JSON, default=[])
    related_searches = Column(JSON, default=[])
    difficulty_proxy = Column(Float, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)

class FileBackup(Base):
    __tablename__ = "file_backups"

    id = Column(Integer, primary_key=True, index=True)
    original_path = Column(String, index=True)
    backup_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class BacklinkSubmission(Base):
    __tablename__ = "backlink_submissions"

    id = Column(Integer, primary_key=True, index=True)
    target_url = Column(String, index=True)
    submitted_url = Column(String, index=True)
    domain = Column(String, index=True)
    anchor_text = Column(String, nullable=True)
    author_name = Column(String, nullable=True)
    author_email = Column(String, nullable=True)
    article_title = Column(String, nullable=True)
    content_snippet = Column(Text, nullable=True)
    link_type = Column(String, default="dofollow") # dofollow, nofollow, ugc, sponsored
    submission_category = Column(String, default="Web 2.0") # Guest Post, Directory, Web 2.0, Bookmarking, Profile, Forum, Comments
    da_score = Column(Integer, default=30)
    status = Column(String, default="pending") # pending, verified, indexed, rejected
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    verified_at = Column(DateTime, nullable=True)

class AutoScheduleConfig(Base):
    __tablename__ = "auto_schedule_configs"

    id = Column(Integer, primary_key=True, index=True)
    target_url = Column(String, default="https://example.com")
    target_keyword = Column(String, default="SEO optimization")
    daily_goal = Column(Integer, default=300)
    is_enabled = Column(Integer, default=1) # 1 for True, 0 for False
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)
class BrandProfile(Base):
    __tablename__ = "brand_profiles"

    id = Column(Integer, primary_key=True, index=True)
    brand_name = Column(String, default="Fairepairs")
    website_url = Column(String, default="https://fairepairs.com/")
    account_email = Column(String, default="fairpayt@gmail.com")
    niche_industry = Column(String, default="Auto Repairs & Services")
    primary_keyword = Column(String, default="SEO optimization guide")
    updated_at = Column(DateTime, default=datetime.utcnow)
