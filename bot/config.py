import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Bot settings
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Database: one absolute file for every process regardless of cwd.
_project_root = Path(__file__).resolve().parents[1]
_default_db = _project_root / 'fitness_bot.db'
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{_default_db}')
if DATABASE_URL.startswith('sqlite:///./'):
    DATABASE_URL = f"sqlite:///{_project_root / DATABASE_URL.replace('sqlite:///./', '')}"
# SQLAlchemy 2.1 defaults PostgreSQL URLs to psycopg (v3). Render installs
# psycopg2-binary, so make the driver explicit for both postgres URL spellings.
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = 'postgresql+psycopg2://' + DATABASE_URL[len('postgres://'):]
elif DATABASE_URL.startswith('postgresql://'):
    DATABASE_URL = 'postgresql+psycopg2://' + DATABASE_URL[len('postgresql://'):]

# DeepSeek AI for text and food-photo analysis.
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '').strip()
DEEPSEEK_API_URL = os.getenv('DEEPSEEK_API_URL', 'https://api.deepseek.com/chat/completions').strip()
DEEPSEEK_TEXT_MODEL = os.getenv('DEEPSEEK_TEXT_MODEL', 'deepseek-chat').strip()
DEEPSEEK_VISION_MODEL = os.getenv('DEEPSEEK_VISION_MODEL', 'deepseek-flash').strip()
AI_REQUEST_TIMEOUT = int(os.getenv('AI_REQUEST_TIMEOUT', '60'))

# Web App
# WEBAPP_URL is local URL for browser development. Telegram requires WEBAPP_PUBLIC_URL.
WEBAPP_URL = os.getenv('WEBAPP_URL', 'http://localhost:8081')
WEBAPP_PUBLIC_URL = os.getenv('WEBAPP_PUBLIC_URL', '').strip()
PUBLIC_SITE_URL = os.getenv('PUBLIC_SITE_URL', '').strip()
if WEBAPP_PUBLIC_URL and not WEBAPP_PUBLIC_URL.startswith(('http://', 'https://')):
    WEBAPP_PUBLIC_URL = f'https://{WEBAPP_PUBLIC_URL}'
WEB_PORT = int(os.getenv('WEB_PORT', 8081))
REQUIRE_WEBAPP_AUTH = os.getenv('REQUIRE_WEBAPP_AUTH', 'True').lower() == 'true'

# Admin dashboard
ADMIN_KEY = os.getenv('ADMIN_KEY', '').strip()
ADMIN_SESSION_SECRET = os.getenv('ADMIN_SESSION_SECRET', '').strip() or (BOT_TOKEN or 'gym-helper-local-secret')

# Environment
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

ACTIVITY_LEVELS = {
    'sedentary': 1.2,
    'light': 1.375,
    'moderate': 1.55,
    'active': 1.725,
    'very_active': 1.9,
}

GOAL_ADJUSTMENTS = {
    'lose_weight': -500,
    'maintain': 0,
    'gain_muscle': 300,
}
