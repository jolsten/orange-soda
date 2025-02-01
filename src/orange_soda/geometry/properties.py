import datetime
from typing import Annotated, Any, Optional

from pydantic import BaseModel, BeforeValidator, PlainSerializer

from orange_soda.alpha5 import from_alpha5, to_alpha5


def decode_satnum(satnum: Any) -> int:
    if isinstance(satnum, int):
        return satnum
    if isinstance(satnum, str):
        return from_alpha5(satnum)
    raise TypeError


def encode_satnum(satnum: Any) -> str:
    if isinstance(satnum, int):
        return to_alpha5(satnum)
    if isinstance(satnum, str):
        return satnum
    raise TypeError


Satnum = Annotated[int, BeforeValidator(decode_satnum), PlainSerializer(encode_satnum)]


class Properties(BaseModel):
    classification: Optional[str] = None
    satnum: Optional[Satnum] = None
    start: Optional[datetime.datetime] = None
    stop: Optional[datetime.datetime] = None
