import redis

from django.conf import settings

cache = redis.Redis(
    host=settings.REDIS_HOST,
    port=int(settings.REDIS_PORT),
    charset="utf-8",
    decode_responses=True,
)
