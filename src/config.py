import os
from dotenv import load_dotenv

load_dotenv()

DB_HOSTNAME = os.getenv("DB_HOSTNAME")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_PORT = os.environ.get("DB_PORT")
DB_NAME = os.environ.get("DB_NAME")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")


def get_engine_url():
    return f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOSTNAME}:{DB_PORT}/{DB_NAME}"
