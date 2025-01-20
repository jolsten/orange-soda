import datetime

from orange_soda.interval import parse_intervals

SAMPLE = """
2025-01-01T00:01:00 2025-01-01T00:02:00 25544
"""


def test_parse_intervals():
    intervals = parse_intervals(SAMPLE)
    for interval in intervals:
        assert isinstance(interval.start, datetime.datetime)
        assert isinstance(interval.stop, datetime.datetime)
        assert isinstance(interval.objnum, str)
