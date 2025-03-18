import os

from dotenv import load_dotenv

load_dotenv()

OPENWA_API_URL = os.getenv("OPENWA_API_URL")
SESSION_NAME = os.getenv("SESSION_NAME")
SUPPORT_GROUP_ID = os.getenv("SUPPORT_GROUP_ID")
