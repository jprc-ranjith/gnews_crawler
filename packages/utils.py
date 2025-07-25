import re
from datetime import datetime, timedelta

def process_url(url):
    cleaned_url = re.sub(r'/|https|:|-', ' ', url)
    return re.sub(r'^\s+|\s+$', '', cleaned_url)

def float_to_dynamic_integer(float_value):
    float_str = str(float_value)
    decimal_point_index = float_str.find('.')
    if decimal_point_index == -1:
        decimal_places = 0
    else:
        decimal_places = len(float_str) - decimal_point_index - 1
    power_of_10 = 10 ** decimal_places
    integer_value = int(float_value * power_of_10)
    return integer_value

def get_url_vecid(url, nlp):
    url_text = process_url(url)
    vec = nlp(url_text)
    vec_norm = vec.vector_norm
    return float_to_dynamic_integer(vec_norm)

def month_range(self, start, end):
    current = start.replace(day=1)
    while current <= end:
        next_month = (current.month % 12) + 1
        next_year = current.year + (current.month // 12)
        month_end = (datetime(next_year, next_month, 1) - timedelta(days=1)) if next_month != 1 else (datetime(current.year, 12, 31))
        yield (current, min(month_end, end))
        current = month_end + timedelta(days=1)

def three_month_range(start: datetime, end: datetime):
    """
    Yields (start, end) date tuples for up to 3-month intervals.
    Handles partial ranges robustly.
    """
    current = start.replace(day=1)
    while current <= end:
        # Find the last day of the 3rd month
        # Add 3 months: if current = Jan, go to April 1st, then -1 day = Mar 31
        if current.month + 3 > 12:
            next_year = current.year + ((current.month + 3 - 1) // 12)
            next_month = ((current.month + 3 - 1) % 12) + 1
        else:
            next_year = current.year
            next_month = current.month + 3
        window_end = datetime(next_year, next_month, 1) - timedelta(days=1)
        # Clamp to end
        range_end = min(window_end, end)
        yield (current, range_end)
        # Advance 3 months
        if current.month > 9:
            current = datetime(current.year + 1, ((current.month + 2) % 12) + 1, 1)
        else:
            current = datetime(current.year, current.month + 3, 1)