from collections import namedtuple

from aiocache.backends.redis import RedisCache
from aiocache.serializers import PickleSerializer


class BotCache(RedisCache):
    def __init__(self, config) -> None:
        super().__init__(
            serializer=PickleSerializer(),
            namespace=config.REDIS_NAMESPACE,
            endpoint=config.REDIS_IP,
            port=config.REDIS_PORT,
            db=config.REDIS_DB,
        )


guildObject = namedtuple("guildObject", "prefix samp minecraft")
