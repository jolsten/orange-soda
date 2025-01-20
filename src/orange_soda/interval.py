import datetime
from dataclasses import dataclass
from typing import Optional, Self, Union

from dateutil.parser import parse as parse_datetime


@dataclass
class Interval:
    objnum: Union[int, str]
    start: datetime.datetime
    stop: datetime.datetime

    category: Optional[str] = None
    color: Optional[float] = None
    size: Optional[float] = None

    @classmethod
    def from_string(cls, input: str) -> Self:
        start, stop, objnum, *rest = input.split()

        kwargs = {}
        for one in rest:
            one = one.replace(":", "=", count=1)
            try:
                kw, arg = one.split("=", maxsplit=1)
                kwargs[kw] = arg
            except ValueError:
                msg = f"keyword argument invalid {one!r}; must be in format KEY=VAL or KEY:VAL"
                raise ValueError(msg)

        start, stop = parse_datetime(start), parse_datetime(stop)
        return cls(objnum=objnum, start=start, stop=stop, **kwargs)


def parse_intervals(text: str) -> list[Interval]:
    intervals = []
    for idx, line in enumerate(text.splitlines()):
        line = line.strip()
        if line:
            intervals.append(Interval.from_string(line))
    return intervals
