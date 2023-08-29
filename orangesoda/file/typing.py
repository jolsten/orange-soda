import datetime
import pathlib
import os
import re
from typing import Literal, Union
try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated
from pydantic import BeforeValidator

PathLike = Union[str, bytes, os.PathLike, pathlib.Path]

def mmddyy_to_date(yymmdd: str) -> datetime.date:
    mm, dd, yy = yymmdd[0:2], yymmdd[2:4], yymmdd[4:6]
    yy, mm, dd = int(yy), int(mm), int(dd)
    if yy < 70:
        yy += 2000
    else:
        yy += 1900
    return datetime.date(yy, mm, dd)

MMDDYY = Annotated[datetime.date, BeforeValidator(mmddyy_to_date)]

def yymmdd_to_date(yymmdd: str) -> datetime.date:
    yy, mm, dd = yymmdd[0:2], yymmdd[2:4], yymmdd[4:6]
    yy, mm, dd = int(yy), int(mm), int(dd)
    if yy < 70:
        yy += 2000
    else:
        yy += 1900
    return datetime.date(yy, mm, dd)

YYMMDD = Annotated[datetime.date, BeforeValidator(yymmdd_to_date)]

def hhmmss_to_time(hhmmss: str) -> datetime.time:
    hh, mm, ss = hhmmss[0:2], hhmmss[2:4], hhmmss[4:6]
    hh, mm, ss = int(hh), int(mm), int(ss)
    return datetime.time(hh, mm, ss)

HHMMSS = Annotated[datetime.time, BeforeValidator(hhmmss_to_time)]

ByteOrder = Annotated[Literal["MSBF", "LSBF"], BeforeValidator(lambda x: x.upper())]

_RE_FLOAT = re.compile(r'(\d+(?:\.\d+))')

def validate_frequency(freq: str) -> float:
    m = _RE_FLOAT.match(freq)
    assert m
    return float(m.groups()[0])

Frequency = Annotated[float, BeforeValidator(validate_frequency)]
