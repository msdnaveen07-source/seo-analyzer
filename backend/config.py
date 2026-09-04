import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(PROJECT_ROOT, 'seo_analyzer.db')}")
CRAWL_DELAY_SECONDS = float(os.getenv("CRAWL_DELAY_SECONDS", "2.0"))
GOOGLE_SCRAPE_DELAY_SECONDS = float(os.getenv("GOOGLE_SCRAPE_DELAY_SECONDS", "10.0"))
LIGHTHOUSE_CLI_PATH = os.getenv("LIGHTHOUSE_CLI_PATH", "lighthouse")
DEFAULT_AUTHOR_EMAIL = os.getenv("DEFAULT_AUTHOR_EMAIL", "fairpayt@gmail.com")
BACKUP_DIR = os.path.join(PROJECT_ROOT, "backups")

os.makedirs(BACKUP_DIR, exist_ok=True)
