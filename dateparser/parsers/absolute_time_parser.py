from calendar import calendar
from collections import OrderedDict
from datetime import datetime, timedelta

import regex as re

from dateparser.parsers import _try_parser, _time_parser_obj, \
    _resolve_date_order
from dateparser.utils import get_next_leap_year, get_previous_leap_year, \
    set_correct_day_from_settings, get_last_day_of_month
from dateparser.utils.string import _Tokenizer
from dateparser.utils.strptime import strptime

HOUR_MINUTE_REGEX = re.compile(r'^([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$')
MICROSECOND = re.compile(r'\d{1,6}')
MERIDIAN = re.compile(r'am|pm')


def parse_absolute_time(date_string, settings, locale):
    return _try_parser(date_string, settings, locale, parse_method=_parse_absolute)


def _parse_absolute(datestring, settings):
    return _AbsoluteTimeParser.parse(datestring, settings)


class _AbsoluteTimeParser:

    alpha_directives = OrderedDict([
        ('weekday', ['%A', '%a']),
        ('month', ['%B', '%b']),
    ])

    num_directives = {
        'month': ['%m'],
        'day': ['%d'],
        'year': ['%y', '%Y'],
    }

    def __init__(self, tokens, settings):
        self.settings = settings
        self.tokens = list(tokens)
        self.filtered_tokens = [(t[0], t[1], i) for i, t in enumerate(self.tokens) if t[1] <= 1]

        self.unset_tokens = []

        self.day = None
        self.month = None
        self.year = None
        self.time = None

        self.auto_order = []

        self._token_day = None
        self._token_month = None
        self._token_year = None
        self._token_time = None

        self.ordered_num_directives = OrderedDict(
            (k, self.num_directives[k])
            for k in (_resolve_date_order(settings.DATE_ORDER, lst=True))
        )

        skip_index = []
        skip_component = None
        skip_tokens = ["t", "year", "hour", "minute"]

        for index, token_type_original_index in enumerate(self.filtered_tokens):

            if index in skip_index:
                continue

            token, type, original_index = token_type_original_index

            if token in skip_tokens:
                continue

            if self.time is None:
                meridian_index = index + 1

                try:
                    # try case where hours and minutes are separated by a period. Example: 13.20.
                    _is_before_period = self.tokens[original_index + 1][0] == '.'
                    _is_after_period = original_index != 0 and self.tokens[original_index - 1][0] == '.'

                    if _is_before_period and not _is_after_period:
                        index_next_token = index + 1
                        next_token = self.filtered_tokens[index_next_token][0]
                        index_in_tokens_for_next_token = self.filtered_tokens[index_next_token][2]

                        next_token_is_last = index_next_token == len(self.filtered_tokens) - 1
                        if next_token_is_last or self.tokens[index_in_tokens_for_next_token + 1][0] != '.':
                            new_token = token + ':' + next_token
                            if re.match(HOUR_MINUTE_REGEX, new_token):
                                token = new_token
                                skip_index.append(index + 1)
                                meridian_index += 1
                except Exception:
                    pass

                try:
                    microsecond = MICROSECOND.search(self.filtered_tokens[index + 1][0]).group()
                    _is_after_time_token = token.index(":")
                    _is_after_period = self.tokens[self.tokens.index((token, 0)) + 1][0].index('.')
                except:
                    microsecond = None

                if microsecond:
                    meridian_index += 1

                try:
                    meridian = MERIDIAN.search(self.filtered_tokens[meridian_index][0]).group()
                except:
                    meridian = None

                if any([':' in token, meridian, microsecond]):
                    if meridian and not microsecond:
                        self._token_time = '%s %s' % (token, meridian)
                        skip_index.append(meridian_index)
                    elif microsecond and not meridian:
                        self._token_time = '%s.%s' % (token, microsecond)
                        skip_index.append(index + 1)
                    elif meridian and microsecond:
                        self._token_time = '%s.%s %s' % (token, microsecond, meridian)
                        skip_index.append(index + 1)
                        skip_index.append(meridian_index)
                    else:
                        self._token_time = token
                    self.time = lambda: _time_parser_obj(self._token_time)
                    continue

            results = self._parse(type, token, settings.FUZZY, skip_component=skip_component)
            for res in results:
                if len(token) == 4 and res[0] == 'year':
                    skip_component = 'year'
                setattr(self, *res)

        known, unknown = _get_unresolved_attrs(self)
        params = {}
        for attr in known:
            params.update({attr: getattr(self, attr)})
        for attr in unknown:
            for token, type, _ in self.unset_tokens:
                if type == 0:
                    params.update({attr: int(token)})
                    setattr(self, '_token_%s' % attr, token)
                    setattr(self, attr, int(token))

    def _get_period(self):
        if self.settings.RETURN_TIME_AS_PERIOD:
            if getattr(self, 'time', None):
                return 'time'

        for period in ['time', 'day']:
            if getattr(self, period, None):
                return 'day'

        for period in ['month', 'year']:
            if getattr(self, period, None):
                return period

        if self._results():
            return 'day'

    def _get_datetime_obj(self, **params):
        try:
            return datetime(**params)
        except ValueError as e:
            error_text = e.__str__()
            error_msgs = ['day is out of range', 'day must be in']
            if (error_msgs[0] in error_text or error_msgs[1] in error_text):
                if not(self._token_day or hasattr(self, '_token_weekday')):
                    # if day is not available put last day of the month
                    params['day'] = get_last_day_of_month(params['year'], params['month'])
                    return datetime(**params)
                elif not self._token_year and params['day'] == 29 and params['month'] == 2 and \
                        not calendar.isleap(params['year']):
                    # fix the year when year is not present and it is 29 of February
                    params['year'] = self._get_correct_leap_year(self.settings.PREFER_DATES_FROM, params['year'])
                    return datetime(**params)
            raise e

    def _get_correct_leap_year(self, prefer_dates_from, current_year):
        if prefer_dates_from == 'future':
            return get_next_leap_year(current_year)
        if prefer_dates_from == 'past':
            return get_previous_leap_year(current_year)

        # Default case ('current_period'): return closer leap year
        next_leap_year = get_next_leap_year(current_year)
        previous_leap_year = get_previous_leap_year(current_year)
        next_leap_year_is_closer = next_leap_year - current_year < current_year - previous_leap_year
        return next_leap_year if next_leap_year_is_closer else previous_leap_year

    def _set_relative_base(self):
        self.now = self.settings.RELATIVE_BASE
        if not self.now:
            self.now = datetime.utcnow()

    def _get_datetime_obj_params(self):
        if not self.now:
            self._set_relative_base()

        params = {
            'day': self.day or self.now.day,
            'month': self.month or self.now.month,
            'year': self.year or self.now.year,
            'hour': 0, 'minute': 0, 'second': 0, 'microsecond': 0,
        }
        return params

    def _get_date_obj(self, token, directive):
        return strptime(token, directive)

    def _missing_error(self, missing):
        return ValueError(
            'Fields missing from the date string: {}'.format(', '.join(missing))
        )

    def _results(self):
        missing = [field for field in ('day', 'month', 'year')
                   if not getattr(self, field)]

        if self.settings.STRICT_PARSING and missing:
            raise self._missing_error(missing)
        elif self.settings.REQUIRE_PARTS and missing:
            errors = [part for part in self.settings.REQUIRE_PARTS if part in missing]
            if errors:
                raise self._missing_error(errors)

        self._set_relative_base()

        time = self.time() if self.time is not None else None

        if self.settings.FUZZY:
            attr_truth_values = []
            for attr in ['day', 'month', 'year', 'time']:
                attr_truth_values.append(getattr(self, attr, False))

            if not any(attr_truth_values):
                raise ValueError('Nothing date like found')

        params = self._get_datetime_obj_params()

        if time:
            params.update(dict(hour=time.hour,
                               minute=time.minute,
                               second=time.second,
                               microsecond=time.microsecond))

        return self._get_datetime_obj(**params)

    def _correct_for_time_frame(self, dateobj):
        days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

        token_weekday, _ = getattr(self, '_token_weekday', (None, None))

        if token_weekday and not(self._token_year or self._token_month or self._token_day):
            day_index = calendar.weekday(dateobj.year, dateobj.month, dateobj.day)
            day = token_weekday[:3].lower()
            steps = 0
            if 'future' in self.settings.PREFER_DATES_FROM:
                if days[day_index] == day:
                    steps = 7
                else:
                    while days[day_index] != day:
                        day_index = (day_index + 1) % 7
                        steps += 1
                delta = timedelta(days=steps)
            else:
                if days[day_index] == day:
                    if self.settings.PREFER_DATES_FROM == 'past':
                        steps = 7
                    else:
                        steps = 0
                else:
                    while days[day_index] != day:
                        day_index -= 1
                        steps += 1
                delta = timedelta(days=-steps)

            dateobj = dateobj + delta

        if self.month and not self.year:
            try:
                if self.now < dateobj:
                    if self.settings.PREFER_DATES_FROM == 'past':
                        dateobj = dateobj.replace(year=dateobj.year - 1)
                else:
                    if self.settings.PREFER_DATES_FROM == 'future':
                        dateobj = dateobj.replace(year=dateobj.year + 1)
            except ValueError as e:
                if dateobj.day == 29 and dateobj.month == 2:
                    valid_year = self._get_correct_leap_year(
                        self.settings.PREFER_DATES_FROM, dateobj.year)
                    dateobj = dateobj.replace(year=valid_year)
                else:
                    raise e

        if self._token_year and len(self._token_year[0]) == 2:
            if self.now < dateobj:
                if 'past' in self.settings.PREFER_DATES_FROM:
                    dateobj = dateobj.replace(year=dateobj.year - 100)
            else:
                if 'future' in self.settings.PREFER_DATES_FROM:
                    dateobj = dateobj.replace(year=dateobj.year + 100)

        if self._token_time and not any([self._token_year,
                                         self._token_month,
                                         self._token_day,
                                         hasattr(self, '_token_weekday')]):
            if 'past' in self.settings.PREFER_DATES_FROM:
                if self.now.time() < dateobj.time():
                    dateobj = dateobj + timedelta(days=-1)
            if 'future' in self.settings.PREFER_DATES_FROM:
                if self.now.time() > dateobj.time():
                    dateobj = dateobj + timedelta(days=1)

        return dateobj

    def _correct_for_day(self, dateobj):
        if (
            getattr(self, '_token_day', None) or
            getattr(self, '_token_weekday', None) or
            getattr(self, '_token_time', None)
        ):
            return dateobj

        dateobj = set_correct_day_from_settings(
            dateobj, self.settings, current_day=self.now.day
        )
        return dateobj

    @classmethod
    def parse(cls, datestring, settings):
        tokens = _Tokenizer(datestring)
        po = cls(tokens.tokenize(), settings)
        dateobj = po._results()

        # correction for past, future if applicable
        dateobj = po._correct_for_time_frame(dateobj)

        # correction for preference of day: beginning, current, end
        dateobj = po._correct_for_day(dateobj)
        period = po._get_period()

        return dateobj, period

    def _parse(self, type, token, fuzzy, skip_component=None):

        def set_and_return(token, type, component, dateobj, skip_date_order=False):
            if not skip_date_order:
                self.auto_order.append(component)
            setattr(self, '_token_%s' % component, (token, type))
            return [(component, getattr(dateobj, component))]

        def parse_number(token, skip_component=None):
            type = 0

            for component, directives in self.ordered_num_directives.items():
                if skip_component == component:
                    continue
                for directive in directives:
                    try:
                        do = self._get_date_obj(token, directive)
                        prev_value = getattr(self, component, None)
                        if not prev_value:
                            return set_and_return(token, type, component, do)
                        else:
                            try:
                                prev_token, prev_type = getattr(self, '_token_%s' % component)
                                if prev_type == type:
                                    do = self._get_date_obj(prev_token, directive)
                            except ValueError:
                                self.unset_tokens.append((prev_token, prev_type, component))
                                return set_and_return(token, type, component, do)
                    except ValueError:
                        pass
            else:
                if not fuzzy:
                    raise ValueError('Unable to parse: %s' % token)
                else:
                    return []

        def parse_alpha(token, skip_component=None):
            type = 1

            for component, directives in self.alpha_directives.items():
                if skip_component == component:
                    continue
                for directive in directives:
                    try:
                        do = self._get_date_obj(token, directive)
                        prev_value = getattr(self, component, None)
                        if not prev_value:
                            return set_and_return(token, type, component, do, skip_date_order=True)
                        elif component == 'month':
                            index = self.auto_order.index('month')
                            self.auto_order[index] = 'day'
                            setattr(self, '_token_day', self._token_month)
                            setattr(self, '_token_month', (token, type))
                            return [(component, getattr(do, component)), ('day', prev_value)]
                    except:
                        pass
            else:
                if not fuzzy:
                    raise ValueError('Unable to parse: %s' % token)
                else:
                    return []

        handlers = {0: parse_number, 1: parse_alpha}
        return handlers[type](token, skip_component)


def _get_unresolved_attrs(parser_object):
    attrs = ['year', 'month', 'day']
    seen = []
    unseen = []
    for attr in attrs:
        if getattr(parser_object, attr, None) is not None:
            seen.append(attr)
        else:
            unseen.append(attr)
    return seen, unseen
