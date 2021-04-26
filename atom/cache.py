from aiocache.backends.redis import RedisCache
from collections import namedtuple
from aiocache.serializers import PickleSerializer


class BotCache(RedisCache):
    def __init__(self, config) -> None:
        super().__init__(
            serializer=PickleSerializer(),
            namespace=config.REDIS_NAMESPACE,
            endpoint=config.REDIS_IP,
            port=config.REDIS_PORT,
        )


guildObject = namedtuple("guildObject", ["prefix", "samp", "minecraft"])
