import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
SITE = "https://app.auvo.com.br/"
USER = os.environ['auvo_USER']
PASS = os.environ['auvo_PASS']
APP_KEY = os.environ['APP_KEY']
TOKEN = os.environ['TOKEN']
EMAIL = os.environ['EMAIL']
E_PASS = os.environ['E_PASS']
TO_EMAIL = os.environ['TO_EMAIL']
SECRET = os.environ['NOTION_SECRET']
DB_ID = os.environ['DB_ID']