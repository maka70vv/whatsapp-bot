import os

import redis
from dotenv import load_dotenv

load_dotenv()

OPENWA_API_URL = os.getenv("OPENWA_API_URL")
SESSION_NAME = os.getenv("SESSION_NAME")

redis_client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, db=0, decode_responses=True)
