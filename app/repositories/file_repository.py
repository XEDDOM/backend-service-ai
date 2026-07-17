from filelock import FileLock
import json, logging
from datetime import datetime
from app.core.config import settings

logger = logging.getLogger(__name__)
stats_file = settings.DATA_DIR / "stats.json"
stats_lock = FileLock(str(stats_file) + ".lock")

def save_stats(is_success: bool, used_fallback: bool):
    with stats_lock:
        try:
            with open(stats_file, "r") as f:
                stats = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            stats = {"total_requests": 0, "successful_contacts": 0, "ai_fallbacks": 0, "last_updated": ""}

        stats["total_requests"] += 1
        if is_success:
            stats["successful_contacts"] += 1
        if used_fallback:
            stats["ai_fallbacks"] += 1
        stats["last_updated"] = datetime.now().isoformat()

        with open(stats_file, "w") as f:
            json.dump(stats, f, indent=4)

def get_stats() -> dict:
    with stats_lock:
        try:
            with open(stats_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"total_requests": 0, "successful_contacts": 0, "ai_fallbacks": 0}
