import typing as T
from ...utils._http import http
from ..._types import CertificatePayload, Template
# from dataclasses import dataclass

class routes:
    @classmethod
    def templates(cls) -> str:
        return "/certificate/templates"
    
    @classmethod
    def generate(cls, template : "CertificateTemplate") -> str:
        return "/certificate/generate?template=" + template.id


class CertificateTemplate:
    """a certificate template, used to generate certificates"""
    name : str
    id : str
    premium : bool

    __cache : T.ClassVar[dict[str, T.Self]] = {}

    def __init__(self, **kwargs: T.Unpack[Template]):
        self.name = kwargs.get("name")
        self.id = kwargs.get("id")
        self.premium = kwargs.get("premium", False)
        self.__class__.__cache[self.id] = self
        self.__kwargs = kwargs

    def __repr__(self) -> str:
        return self.__kwargs.__repr__()
    
    def __str__(self) -> str:
        return self.__repr__()

    async def generate(self, raw:int=0, **payload : T.Unpack[CertificatePayload]) -> bytes | str:
        "generates a certificate from the template, returns a buffer of the image"
        _response = await http.post(f"{routes.generate(self)}&raw={raw}", json=payload)
        if _response.status != 200:
            raise Exception("Failed to generate certificate: " + (await _response.text()))
        if raw == 1:
            return await _response.read()
        return await _response.text()
    
    @classmethod
    async def all(cls) -> T.List[T.Self]:
        _response = await http.get(routes.templates())
        if _response.status != 200:
            raise Exception("Failed to fetch certificate templates: " + (await _response.text()))

        data = await _response.json()
        return [cls(**template) for template in data]

    @classmethod
    async def get(cls, id: str) -> T.Self | None:
        _exists = cls.__cache.get(id)
        if _exists is not None:
            return _exists
        
        _url = f"{routes.templates()}?id={id}"
        _response = await http.get(_url)

        if _response.status != 200:
            return None
        
        data = await _response.json()

        if data is None:
            return None
        
        return cls(**data)

