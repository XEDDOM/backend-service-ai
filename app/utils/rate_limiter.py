from fastapi import HTTPException
from app.core.config import settings
from filelock import FileLock
import json, time

lock_file = settings.DATA_DIR / "rate_limit.lock"
data_file = settings.DATA_DIR / "rate_limit.json"

def check_rate_limit(client_ip: str):
    lock = FileLock(str(lock_file))
    with lock:
        try:
            with open(data_file, "r") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        current_time = time.time()
        if client_ip in data:
            requests = data[client_ip]
            requests = [t for t in requests if current_time - t < settings.RATE_LIMIT_WINDOW_SECONDS]
            data[client_ip] = requests
        else:
            data[client_ip] = []

        if len(data[client_ip]) >= settings.RATE_LIMIT_MAX_REQUESTS:
            raise HTTPException(status_code=429, detail="Слишком много запросов. Попробуйте позже.")

        data[client_ip].append(current_time)
        with open(data_file, "w") as f:
            json.dump(data, f)
