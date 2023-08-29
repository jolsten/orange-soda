import datetime
from hypothesis import given, strategies as st
from orangesoda.file.typing import yymmdd_to_date, mmddyy_to_date


valid_date = st.dates(
    min_value=datetime.date(1970, 1, 1), max_value=datetime.date(2060, 12, 31)
)


@given(valid_date)
def test_yymmdd(date: datetime.date) -> None:
    yymmdd = date.strftime("%y%m%d")
    assert date == yymmdd_to_date(yymmdd)


@given(valid_date)
def test_mmddyy(date: datetime.date) -> None:
    yymmdd = date.strftime("%m%d%y")
    assert date == mmddyy_to_date(yymmdd)
