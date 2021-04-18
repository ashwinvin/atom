import typing


class BotCache(dict):

    __getattr__ = dict.__getitem__
    __delattr__ = dict.__delitem__

    def __setattr__(self, name: str, value: typing.Any) -> None:
        self.__dict__[name] = value
