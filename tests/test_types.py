import datetime
from hypothesis import given, strategies as st
from orangesoda.typing import yymmdd_to_date, mmddyy_to_date
from .conftest import valid_date

@given(valid_date)
def test_yymmdd(date: datetime.date) -> None:
    yymmdd = date.strftime('%y%m%d')
    assert date == yymmdd_to_date(yymmdd)

@given(valid_date)
def test_mmddyy(date: datetime.date) -> None:
    yymmdd = date.strftime('%m%d%y')
    assert date == mmddyy_to_date(yymmdd)
