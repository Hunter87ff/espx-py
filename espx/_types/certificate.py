from .utility import Socials
import typing as T



class CertificatePayload(T.TypedDict, total=False):
    organizer: str
    orglogo: T.Optional[str]
    eventname : str
    date: T.Optional[str]
    name: str
    rank : int
    signature: T.Optional[str]
    social : T.Optional[Socials]


class Template(T.TypedDict):
    name: str
    id: str
    premium: bool
