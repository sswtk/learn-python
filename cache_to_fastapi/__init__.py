"""
@Time    : 2022/3/1 10:56
@Author  : ssw
@File    : __init__.py.py
@Desc    :
"""


import abc
from typing import Tuple


class CacheBase:
    @abc.abstractmethod
    async def get_with_ttl(self, key: str) -> Tuple[int, str]:
        raise NotImplementedError

    @abc.abstractmethod
    async def get(self, key: str) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    async def set(self, key: str, value: str, expire: int = None):
        raise NotImplementedError

    @abc.abstractmethod
    async def clear(self, namespace: str = None, key: str = None) -> int:
        raise NotImplementedError