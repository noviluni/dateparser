import re
from datetime import datetime

from dateparser.utils import apply_timezone_from_settings

RE_SEARCH_TIMESTAMP = re.compile(r'^(\d{10})(\d{3})?(\d{3})?(?![^.])')


def parse_timestamp(
    locale, date_string, translated_date_string, translated_date_string_with_formatting, date_formats, settings
):
    return {
        'date_obj': get_date_from_timestamp(date_string, settings),
        'period': 'day',
    }


def get_date_from_timestamp(date_string, settings):
    match = RE_SEARCH_TIMESTAMP.search(date_string)
    if match:
        seconds = int(match.group(1))
        millis = int(match.group(2) or 0)
        micros = int(match.group(3) or 0)
        date_obj = datetime.fromtimestamp(seconds)
        date_obj = date_obj.replace(microsecond=millis * 1000 + micros)
        date_obj = apply_timezone_from_settings(date_obj, settings)
        return date_obj
