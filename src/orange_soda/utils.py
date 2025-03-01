import collections
import datetime
import math
from typing import Union

from thistle.alpha5 import from_alpha5, to_alpha5

MEAN_EARTH_RADIUS = {"m": 6_371_000, "km": 6_371_000}


Coordinate = collections.namedtuple(
    "Coordinate", ["lat", "lon", "alt"], defaults=[None]
)

Coordinates = Union[tuple[float, float], tuple[float, float, float]]


def radians(ang: float) -> float:
    return ang * math.pi / 180


def degrees(ang: float) -> float:
    return ang * 180 / math.pi


def encode_satnum(satnum) -> str:
    if isinstance(satnum, int):
        return to_alpha5(satnum)
    if isinstance(satnum, str):
        return satnum
    raise TypeError


def decode_satnum(satnum) -> int:
    if isinstance(satnum, int):
        return satnum
    if isinstance(satnum, str):
        return from_alpha5(satnum)
    raise TypeError


def ensure_utc(time: datetime.datetime) -> datetime.datetime:
    """Convert a datetime.datetime to UTC.

    If there is no timezone information, assume the time is UTC.
    """
    if time.tzinfo is None:
        time = time.replace(tzinfo=datetime.timezone.utc)
    else:
        time = time.astimezone(datetime.timezone.utc)
    return time


def trange(
    start: datetime.datetime, stop: datetime.datetime, step: float
) -> list[datetime.datetime]:
    start = ensure_utc(start)
    stop = ensure_utc(stop)
    step = datetime.timedelta(seconds=step)
    times = []
    while start < stop:
        times.append(start)
        start += step
    return times
