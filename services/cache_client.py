import redis
import os

class CacheClient:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL")

        if redis_url:
            # ✅ Production (Render)
            self.client = redis.from_url(redis_url, decode_responses=True)
            print("Connected to Redis (Render)")
        else:
            # ✅ Local fallback
            self.client = redis.Redis(
                host="localhost",
                port=6379,
                db=0,
                decode_responses=True
            )
            print("Connected to Redis (Local)")

        self.hit = 0
        self.miss = 0

    def get(self, key):
        try:
            value = self.client.get(key)

            if value:
                self.hit += 1
                print("cache hit")
            else:
                self.miss += 1
                print("cache miss")

            return value
        except Exception as e:
            print("Redis GET error:", e)
            return None

    def set(self, key, value, ttl=900):
        try:
            self.client.setex(key, ttl, value)
        except Exception as e:
            print("Redis SET error:", e)

    def get_stats(self):
        return {
            "hits": self.hit,
            "miss": self.miss
        }