import collections
from collections.abc import Set
from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from dateparser.languages.loader import LocaleDataLoader
from dateparser.conf import apply_settings
from dateparser.parsers import existing_parsers
from dateparser.parsers.custom_formats_parser import _parse_with_formats
from dateparser.parsers.timestamp_parser import _get_date_from_timestamp
from dateparser.timezone_parser import pop_tz_offset_from_string
from dateparser.utils.string import sanitize_date as _sanitize_date, \
    sanitize_spaces as _sanitize_spaces, _APOSTROPHE_LOOK_ALIKE_CHARS, \
    _RE_NBSP, _RE_SPACES, _RE_TRIM_SPACES, _RE_TRIM_COLONS, _RE_SANITIZE_SKIP, \
    _RE_SANITIZE_RUSSIAN, _RE_SANITIZE_PERIOD, _RE_SANITIZE_ON, \
    _RE_SANITIZE_APOSTROPHE

APOSTROPHE_LOOK_ALIKE_CHARS = _APOSTROPHE_LOOK_ALIKE_CHARS  # TODO: add deprecation warning
RE_NBSP = _RE_NBSP  # TODO: add deprecation warning
RE_SPACES = _RE_SPACES  # TODO: add deprecation warning
RE_TRIM_SPACES = _RE_TRIM_SPACES  # TODO: add deprecation warning
RE_TRIM_COLONS = _RE_TRIM_COLONS  # TODO: add deprecation warning
RE_SANITIZE_SKIP = _RE_SANITIZE_SKIP  # TODO: add deprecation warning
RE_SANITIZE_RUSSIAN = _RE_SANITIZE_RUSSIAN  # TODO: add deprecation warning
RE_SANITIZE_PERIOD = _RE_SANITIZE_PERIOD  # TODO: add deprecation warning
RE_SANITIZE_ON = _RE_SANITIZE_ON  # TODO: add deprecation warning
RE_SANITIZE_APOSTROPHE = _RE_SANITIZE_APOSTROPHE  # TODO: add deprecation warning


def sanitize_spaces(date_string):
    # TODO: add deprecation warning
    return _sanitize_spaces(date_string)


def date_range(begin, end, **kwargs):
    # TODO: This is not used: deprecate or move to utils?
    dateutil_error_prone_args = ['year', 'month', 'week', 'day', 'hour',
                                 'minute', 'second']
    for arg in dateutil_error_prone_args:
        if arg in kwargs:
            raise ValueError("Invalid argument: %s" % arg)

    step = relativedelta(**kwargs) if kwargs else relativedelta(days=1)

    date = begin
    while date < end:
        yield date
        date += step

    # handles edge-case when iterating months and last interval is < 30 days
    if kwargs.get('months', 0) > 0 and (date.year, date.month) == (end.year, end.month):
        yield end


def get_intersecting_periods(low, high, period='day'):
    # TODO: This is not used: deprecate or move to utils?
    if period not in ['year', 'month', 'week', 'day', 'hour', 'minute', 'second', 'microsecond']:
        raise ValueError("Invalid period: {}".format(period))

    if high <= low:
        return

    step = relativedelta(**{period + 's': 1})

    current_period_start = low
    if isinstance(current_period_start, datetime):
        reset_arguments = {}
        for test_period in ['microsecond', 'second', 'minute', 'hour']:
            if test_period == period:
                break
            else:
                reset_arguments[test_period] = 0
        current_period_start = current_period_start.replace(**reset_arguments)

    if period == 'week':
        current_period_start \
            = current_period_start - timedelta(days=current_period_start.weekday())
    elif period == 'month':
        current_period_start = current_period_start.replace(day=1)
    elif period == 'year':
        current_period_start = current_period_start.replace(month=1, day=1)

    while current_period_start < high:
        yield current_period_start
        current_period_start += step


def get_date_from_timestamp(date_string, settings):
    # TODO: add deprecation warning
    return _get_date_from_timestamp(date_string, settings)


def sanitize_date(date_string):
    # TODO: add deprecation warning
    return _sanitize_date(date_string)


def parse_with_formats(date_string, date_formats, settings):
    # TODO: add deprecation warning
    return _parse_with_formats(date_string, date_formats, settings)


class DateDataParser:
    """
    Class which handles language detection, translation and subsequent generic parsing of
    string representing date and/or time.

    :param languages:
        A list of language codes, e.g. ['en', 'es', 'zh-Hant'].
        If locales are not given, languages and region are
        used to construct locales for translation.
    :type languages: list

    :param locales:
        A list of locale codes, e.g. ['fr-PF', 'qu-EC', 'af-NA'].
        The parser uses locales to translate date string.
    :type locales: list

    :param region:
        A region code, e.g. 'IN', '001', 'NE'.
        If locales are not given, languages and region are
        used to construct locales for translation.
    :type region: str

    :param try_previous_locales:
        If True, locales previously used to translate date are tried first.
    :type try_previous_locales: bool

    :param use_given_order:
        If True, locales are tried for translation of date string
        in the order in which they are given.
    :type use_given_order: bool

    :param settings:
        Configure customized behavior using settings defined in :mod:`dateparser.conf.Settings`.
    :type settings: dict

    :return: A parser instance

    :raises:
        ValueError - Unknown Language, TypeError - Languages argument must be a list
    """

    locale_loader = None

    @apply_settings
    def __init__(self, languages=None, locales=None, region=None, try_previous_locales=False,
                 use_given_order=False, settings=None):

        if languages is not None and not isinstance(languages, (list, tuple, Set)):
            raise TypeError("languages argument must be a list (%r given)" % type(languages))

        if locales is not None and not isinstance(locales, (list, tuple, Set)):
            raise TypeError("locales argument must be a list (%r given)" % type(locales))

        if region is not None and not isinstance(region, str):
            raise TypeError("region argument must be str (%r given)" % type(region))

        if not isinstance(try_previous_locales, bool):
            raise TypeError("try_previous_locales argument must be a boolean (%r given)"
                            % type(try_previous_locales))

        if not isinstance(use_given_order, bool):
            raise TypeError("use_given_order argument must be a boolean (%r given)"
                            % type(use_given_order))

        if not locales and use_given_order:
            raise ValueError("locales must be given if use_given_order is True")

        unknown_parsers = set(settings.PARSERS) - set(existing_parsers.keys())
        if unknown_parsers:
            raise ValueError(
                'Unknown parsers found in the PARSERS setting: {}'.format(
                    ', '.join(sorted(unknown_parsers))
                )
            )

        # if not (date_formats is None or isinstance(date_formats, (list, tuple, Set))):
        #           raise TypeError("Date formats should be list, tuple or set of strings")

        self._settings = settings
        self.try_previous_locales = try_previous_locales
        self.use_given_order = use_given_order
        self.languages = languages
        self.locales = locales
        self.region = region
        self.previous_locales = set()

    def get_date_data(self, date_string, date_formats=None):
        """
        Parse string representing date and/or time in recognizable localized formats.
        Supports parsing multiple languages and timezones.

        :param date_string:
            A string representing date and/or time in a recognizably valid format.
        :type date_string: str
        :param date_formats:
            A list of format strings using directives as given
            `here <https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior>`_.
            The parser applies formats one by one, taking into account the detected languages.
        :type date_formats: list

        :return: a dict mapping keys to :mod:`datetime.datetime` object and *period*. For example:
            {'date_obj': datetime.datetime(2015, 6, 1, 0, 0), 'period': 'day'}

        :raises: ValueError - Unknown Language

        .. note:: *Period* values can be a 'day' (default), 'week', 'month', 'year'.

        *Period* represents the granularity of date parsed from the given string.

        In the example below, since no day information is present, the day is assumed to be current
        day ``16`` from *current date* (which is June 16, 2015, at the moment of writing this).
        Hence, the level of precision is ``month``:

            >>> DateDataParser().get_date_data('March 2015')
            {'date_obj': datetime.datetime(2015, 3, 16, 0, 0), 'period': 'month'}

        Similarly, for date strings with no day and month information present, level of precision
        is ``year`` and day ``16`` and month ``6`` are from *current_date*.

            >>> DateDataParser().get_date_data('2014')
            {'date_obj': datetime.datetime(2014, 6, 16, 0, 0), 'period': 'year'}

        Dates with time zone indications or UTC offsets are returned in UTC time unless
        specified using `Settings`_.

            >>> DateDataParser().get_date_data('23 March 2000, 1:21 PM CET')
            {'date_obj': datetime.datetime(2000, 3, 23, 14, 21), 'period': 'day'}

        """
        if not isinstance(date_string, str):
            raise TypeError('Input type must be str')

        # res = parse_with_formats(date_string, date_formats or [], self._settings)
        # if res['date_obj']:
        #     return res

        date_string = sanitize_date(date_string)

        for locale in self._get_applicable_locales(date_string):
            for parser in self._settings.PARSERS:
                parsed_date = existing_parsers[parser](
                    date_string, settings=self._settings, locale=locale
                )  # TODO: Add date_formats?
                if parsed_date and self._is_valid_date_obj(parsed_date):
                    parsed_date['locale'] = locale.shortname
                    if self.try_previous_locales:
                        self.previous_locales.add(locale)
                    return parsed_date
        return {'date_obj': None, 'period': 'day', 'locale': None}

    def get_date_tuple(self, *args, **kwargs):
        date_tuple = collections.namedtuple('DateData', 'date_obj period locale')
        date_data = self.get_date_data(*args, **kwargs)
        return date_tuple(**date_data)

    def _get_applicable_locales(self, date_string):
        pop_tz_cache = []

        def date_strings():
            """ A generator instead of a static list to avoid calling
            pop_tz_offset_from_string if the first locale matches on unmodified
            date_string.
            """
            yield date_string
            if not pop_tz_cache:
                stripped_date_string, _ = pop_tz_offset_from_string(
                    date_string, as_offset=False)
                if stripped_date_string == date_string:
                    stripped_date_string = None
                pop_tz_cache[:] = [stripped_date_string]
            stripped_date_string, = pop_tz_cache
            if stripped_date_string is not None:
                yield stripped_date_string

        if self.try_previous_locales:
            for locale in self.previous_locales:
                for s in date_strings():
                    if self._is_applicable_locale(locale, s):
                        yield locale

        for locale in self._get_locale_loader().get_locales(
                languages=self.languages, locales=self.locales, region=self.region,
                use_given_order=self.use_given_order):
            for s in date_strings():
                if self._is_applicable_locale(locale, s):
                    yield locale

    def _is_applicable_locale(self, locale, date_string):
        return locale.is_applicable(
            date_string,
            strip_timezone=False,  # it is stripped outside
            settings=self._settings)

    @classmethod
    def _get_locale_loader(cls):
        if not cls.locale_loader:
            cls.locale_loader = LocaleDataLoader()
        return cls.locale_loader

    def _is_valid_date_obj(self, date_obj):
        if not isinstance(date_obj, dict):
            return False
        if len(date_obj) != 2:
            return False
        if 'date_obj' not in date_obj or 'period' not in date_obj:
            return False
        if not date_obj['date_obj']:
            return False
        if date_obj['period'] not in ('time', 'day', 'week', 'month', 'year'):
            return False
        return True
