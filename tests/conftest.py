import datetime
from hypothesis import strategies as st

valid_date = st.dates(min_value=datetime.date(1970,1,1), max_value=datetime.date(2060,12,31))
