from dateparser.date_parser import date_parser
from dateparser.utils.strptime import strptime


def _get_translated_date(locale, date_string, keep_formatting, settings):
    return locale.translate(date_string, keep_formatting=keep_formatting, settings=settings)


def _try_parser(date_string, settings, locale, parse_method):
    _order = settings.DATE_ORDER
    try:
        if settings.PREFER_LOCALE_DATE_ORDER:
            if 'DATE_ORDER' not in settings._mod_settings:
                settings.DATE_ORDER = locale.info.get('date_order', _order)
        date_obj, period = date_parser.parse(
            _get_translated_date(locale, date_string, False, settings), parse_method=parse_method, settings=settings
        )
        settings.DATE_ORDER = _order
        return {
            'date_obj': date_obj,
            'period': period,
        }
    except ValueError:
        settings.DATE_ORDER = _order
        return None


def _resolve_date_order(order, lst=None):
    chart = {
        'MDY': '%m%d%y',
        'MYD': '%m%y%d',
        'YMD': '%y%m%d',
        'YDM': '%y%d%m',
        'DMY': '%d%m%y',
        'DYM': '%d%y%m',
    }

    chart_list = {
        'MDY': ['month', 'day', 'year'],
        'MYD': ['month', 'year', 'day'],
        'YMD': ['year', 'month', 'day'],
        'YDM': ['year', 'day', 'month'],
        'DMY': ['day', 'month', 'year'],
        'DYM': ['day', 'year', 'month'],
    }

    return chart_list[order] if lst else chart[order]


class _TimeParser:
    time_directives = [
        '%H:%M:%S',
        '%I:%M:%S %p',
        '%H:%M',
        '%I:%M %p',
        '%I %p',
        '%H:%M:%S.%f',
        '%I:%M:%S.%f %p',
        '%H:%M %p'
    ]

    def __call__(self, timestring):
        _timestring = timestring
        for directive in self.time_directives:
            try:
                return strptime(timestring.strip(), directive).time()
            except ValueError:
                pass
        else:
            raise ValueError('%s does not seem to be a valid time string' % _timestring)


_time_parser_obj = _TimeParser()


# Imports here to avoid circular dependencies
from dateparser.parsers.absolute_time_parser import parse_absolute_time
from dateparser.parsers.custom_formats_parser import parse_custom_formats
from dateparser.parsers.no_spaces_time_parser import parse_no_spaces_time
from dateparser.parsers.relative_time_parser import parse_relative_time
from dateparser.parsers.timestamp_parser import parse_timestamp


existing_parsers = {
    'timestamp': parse_timestamp,
    'relative-time': parse_relative_time,
    'custom-formats': parse_custom_formats,
    'absolute-time': parse_absolute_time,
    'no-spaces-time': parse_no_spaces_time,
}
