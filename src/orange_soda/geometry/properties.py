import datetime
from dataclasses import dataclass
from typing import Any, Optional

from thistle.alpha5 import from_alpha5, to_alpha5


def encode_satnum(satnum: Any) -> str:
    if isinstance(satnum, int):
        return to_alpha5(satnum)
    if isinstance(satnum, str):
        return satnum
    raise TypeError


def decode_satnum(satnum: Any) -> int:
    if isinstance(satnum, int):
        return satnum
    if isinstance(satnum, str):
        return from_alpha5(satnum)
    raise TypeError


@dataclass
class Properties:
    classification: Optional[str] = None
    satnum: Optional[str] = None
    start: Optional[datetime.datetime] = None
    stop: Optional[datetime.datetime] = None

    def __post_init__(self) -> None:
        self.satnum = encode_satnum(self.satnum)
