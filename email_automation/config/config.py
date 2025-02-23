import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
TEMPLATE_DIR = BASE_DIR / "templates"
LOG_DIR = BASE_DIR / "logs"
CONFIG_DIR = BASE_DIR / "config"

# Ensure log directory exists
LOG_DIR.mkdir(exist_ok=True)

# Google Sheets configuration
SPREADSHEET_NAME = os.getenv('SPREADSHEET_NAME', 'Email Campaign Tracker')
WORKSHEET_NAME = os.getenv('WORKSHEET_NAME', 'Campaign Data')

# Email configuration
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_NAME = os.getenv('SENDER_NAME')

# Time intervals (in days) for follow-up emails
FOLLOWUP_1_DELAY = int(os.getenv('FOLLOWUP_1_DELAY', '1'))
FOLLOWUP_2_DELAY = int(os.getenv('FOLLOWUP_2_DELAY', '1'))

# Logging configuration
LOG_FILE = LOG_DIR / "email_log.txt"
ERROR_LOG_FILE = LOG_DIR / "error_log.txt"

# API scopes
GMAIL_SCOPES = ['https://mail.google.com/']
SHEETS_SCOPES = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

# Credentials file paths
CREDENTIALS_FILE = CONFIG_DIR / "credentials.json"
TOKEN_FILE = CONFIG_DIR / "token.json"

# Validate required configuration
if not SENDER_EMAIL:
    raise ValueError("SENDER_EMAIL must be set in .env file")
if not SENDER_NAME:
    raise ValueError("SENDER_NAME must be set in .env file")
if not CREDENTIALS_FILE.exists():
    raise FileNotFoundError(f"Credentials file not found at {CREDENTIALS_FILE}")
if not TEMPLATE_DIR.exists():
    raise FileNotFoundError(f"Template directory not found at {TEMPLATE_DIR}") 