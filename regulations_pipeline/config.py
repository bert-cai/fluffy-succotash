import os
import logging
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

REGULATIONS_GOV_API_KEY = os.environ.get("REGULATIONS_GOV_API_KEY", "")
BASE_URL = "https://api.regulations.gov/v4"
FR_BASE_URL = "https://www.federalregister.gov/api/v1"
DB_PATH = os.environ.get("PIPELINE_DB_PATH", str(Path(__file__).parent.parent / "pipeline_cache.db"))
RATE_LIMIT_PAUSE_SECONDS = 5
MAX_RETRIES = 2
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
