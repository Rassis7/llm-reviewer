import redis
import os
import json
from typing import Dict, List

port = os.environ["REDIS_PORT"]
host = os.environ["REDIS_HOST"]
db = os.environ["REDIS_DB"]


def get_redis_client():
    client = redis.Redis(host=host, port=port, db=db)
    return client


def set(value: Dict[str, str], key: str) -> None:
    client = get_redis_client()
    if client:
        json_value = json.dumps(value)
        client.set(key, json_value)
    else:
        print("Failed to set value in Redis: No client available")


def get(key: str) -> Dict[str, str] | None:
    client = get_redis_client()
    if client:
        value = client.get(key)
        if value:
            json_value = json.loads(value.decode("utf-8"))
            print(f"Got value from Redis: {json_value}")
            return json_value
        else:
            print(f"No value found for key: {key}")
            return None
    else:
        print("Failed to get value from Redis: No client available")
        return None


def get_all(key: str) -> List[Dict[str, str]] | None:
    client = get_redis_client()
    if client:
        keys = client.scan_iter(f"{key}*")
        values = [json.loads(client.get(key).decode("utf-8")) for key in keys]
        print(f"Got all keys from Redis")
        return values
    else:
        print("Failed to get all values from Redis: No client available")
        return None
