import os

from dotenv import load_dotenv
from sqlalchemy.engine import URL

load_dotenv()

required_vars = ["POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB"]

for var in required_vars:
    if not os.environ.get(var):
        raise RuntimeError(f"Missing required environment variable: {var}")

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
    host=os.getenv("POSTGRES_HOST", "localhost"),
    port=int(os.getenv("POSTGRES_PORT", "5432")),
    database=os.environ["POSTGRES_DB"],
)