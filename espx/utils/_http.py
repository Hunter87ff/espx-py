from .._config import apikey, endpoint
import aiohttp
import typing as T
from aiohttp.client import _RequestOptions


def _url(url: str):
    return  endpoint + url

headers = {
    "Authorization" : apikey
}

class http:
    @classmethod
    async def get(cls, url: str, **kwargs : T.Unpack[_RequestOptions]):
        _session = aiohttp.ClientSession()
        kwargs["headers"] = headers
        _response = await _session.get(_url(url), **kwargs)
        await _session.close()
        return _response

    @classmethod
    async def post(cls, url: str, **kwargs : T.Unpack[_RequestOptions]):
        _session = aiohttp.ClientSession()
        kwargs["headers"] = headers
        _response = await _session.post(_url(url), **kwargs)
        await _session.close()
        return _response

    @classmethod
    async def put(cls, url: str, **kwargs : T.Unpack[_RequestOptions]):
        _session = aiohttp.ClientSession()
        kwargs["headers"] = headers
        _response = await _session.put(_url(url), **kwargs)
        await _session.close()
        return _response

    @classmethod
    async def delete(cls, url: str, **kwargs : T.Unpack[_RequestOptions]):
        _session = aiohttp.ClientSession()
        kwargs["headers"] = headers
        _response = await _session.delete(_url(url), **kwargs)
        await _session.close()
        return _response