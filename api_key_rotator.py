import itertools
import time
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read environment variables
api_key1 = os.getenv("GOOGLE_API_KEY")
api_key2 = os.getenv("GOOGLE_API_KEY2")
api_key3 = os.getenv("GOOGLE_API_KEY3")

API_KEYS = []

# Append keys from environment variables to the list
for api_key in [api_key1, api_key2, api_key3]:
    if api_key:
        print(f"✅ Found API Key: {api_key[:4]}...")
        API_KEYS.append({"key": api_key, "req_timestamps": []})
    else:
        print("⚠️ API Key not set for an environment variable.")

# Use a default key if no environment variables are set
if not API_KEYS:
    print("❌ No API keys found in environment variables. Using a placeholder key.")
    API_KEYS.append({"key": "your_fallback_api_key_here", "req_timestamps": []})

key_cycle = itertools.cycle(API_KEYS)
MAX_REQS_PER_MIN = 5

def cleanup_usage(key_info):
    """Remove requests older than 60s."""
    now = time.time()
    key_info["req_timestamps"] = [
        t for t in key_info["req_timestamps"] if now - t < 60
    ]

def get_api_key(auto_wait=True):
    """Return an API key that has quota. Waits if needed."""
    while True:
        for _ in range(len(API_KEYS)):
            key_info = next(key_cycle)
            cleanup_usage(key_info)

            if len(key_info["req_timestamps"]) < MAX_REQS_PER_MIN:
                key_info["req_timestamps"].append(time.time())
                return key_info["key"]

        if auto_wait:
            # Find soonest timestamp that will expire
            next_free_time = min(
                min(k["req_timestamps"]) for k in API_KEYS if k["req_timestamps"]
            )
            sleep_for = max(0, 60 - (time.time() - next_free_time))
            print(f"⏳ All keys exhausted. Waiting {sleep_for:.1f}s...")
            time.sleep(sleep_for + 0.1)
        else:
            raise RuntimeError("🚨 All API keys hit 5 req/min limit")

# Example usage:
if __name__ == "__main__":
    print(f"Loaded {len(API_KEYS)} API key(s) for rotation.")
    for i in range(10):
        key = get_api_key()
        print(f"Request {i+1}: Using key ending in ...{key[-4:]}")
        time.sleep(1) # Simulate an API call