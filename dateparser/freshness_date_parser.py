# TODO: Add deprecation warning to the whole file

from .parsers.relative_time_parser import _RelativeTimeParser, PATTERN as _PATTERN

PATTERN = _PATTERN  # TODO: add deprecation warning


class FreshnessDateDataParser(_RelativeTimeParser):
    # TODO: add deprecation warning
    pass


freshness_date_parser = _RelativeTimeParser()  # TODO: add deprecation warning
