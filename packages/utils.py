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
    Handles partial ranges (e.g., 1, 2, 4, 7 months) robustly.
    """
    current = start.replace(day=1)
    while current <= end:
        # Calculate quarter end
        next_month = current.month + 2
        next_year = current.year
        if next_month > 12:
            next_month -= 12
            next_year += 1
        # The end of the 3rd month in the window
        quarter_end = datetime(next_year, next_month, 1) + timedelta(days=-1)
        # Clamp to user-provided end date
        range_end = min(quarter_end, end)
        yield (current, range_end)
        # Advance 3 months
        if current.month >= 10:
            current = datetime(current.year + 1, ((current.month + 2) % 12) + 1, 1)
        else:
            current = datetime(current.year, current.month + 3, 1)