import regex as re

from dateparser.parsers import _try_parser, _resolve_date_order
from dateparser.utils.string import _Tokenizer
from dateparser.utils.strptime import strptime


EIGHT_DIGIT = re.compile(r'^\d{8}$')
NSP_COMPATIBLE = re.compile(r'\D+')


def parse_no_spaces_time(date_string, settings, locale):
    return _try_parser(date_string, settings, locale, parse_method=_parse_nospaces)


def _parse_nospaces(date_string, settings):
    return _NoSpacesTimeParser.parse(date_string, settings)


def _no_space_parser_eligibile(datestring):
    src = NSP_COMPATIBLE.search(datestring)
    if not src or ':' == src.group():
        return True
    return False


class _NoSpacesTimeParser:
    _dateformats = [
        '%Y%m%d', '%Y%d%m', '%m%Y%d',
        '%m%d%Y', '%d%Y%m', '%d%m%Y',
        '%y%m%d', '%y%d%m', '%m%y%d',
        '%m%d%y', '%d%y%m', '%d%m%y'
    ]

    _preferred_formats = ['%Y%m%d%H%M', '%Y%m%d%H%M%S', '%Y%m%d%H%M%S.%f']

    _preferred_formats_ordered_8_digit = ['%m%d%Y', '%d%m%Y', '%Y%m%d', '%Y%d%m', '%m%Y%d', '%d%Y%m']

    _timeformats = ['%H%M%S.%f', '%H%M%S', '%H%M', '%H']

    period = {
        'day': ['%d', '%H', '%M', '%S'],
        'month': ['%m']
    }

    _default_order = _resolve_date_order('MDY')

    def __init__(self, *args, **kwargs):

        self._all = (self._dateformats +
                     [x + y for x in self._dateformats for y in self._timeformats] +
                     self._timeformats)

        self.date_formats = {
            '%m%d%y': (
                self._preferred_formats +
                sorted(self._all, key=lambda x: x.lower().startswith('%m%d%y'), reverse=True)
            ),
            '%m%y%d': sorted(self._all, key=lambda x: x.lower().startswith('%m%y%d'), reverse=True),
            '%y%m%d': sorted(self._all, key=lambda x: x.lower().startswith('%y%m%d'), reverse=True),
            '%y%d%m': sorted(self._all, key=lambda x: x.lower().startswith('%y%d%m'), reverse=True),
            '%d%m%y': sorted(self._all, key=lambda x: x.lower().startswith('%d%m%y'), reverse=True),
            '%d%y%m': sorted(self._all, key=lambda x: x.lower().startswith('%d%y%m'), reverse=True),
        }

    @classmethod
    def _get_period(cls, format_string):
        for pname, pdrv in sorted(cls.period.items(), key=lambda x: x[0]):
            for drv in pdrv:
                if drv in format_string:
                    return pname
        else:
            return 'year'

    @classmethod
    def _find_best_matching_date(cls, datestring):
        for fmt in cls._preferred_formats_ordered_8_digit:
            try:
                dt = strptime(datestring, fmt), cls._get_period(fmt)
                if len(str(dt[0].year)) == 4:
                    return dt
            except:
                pass
        return None

    @classmethod
    def parse(cls, datestring, settings):
        if not _no_space_parser_eligibile(datestring):
            raise ValueError('Unable to parse date from: %s' % datestring)

        datestring = datestring.replace(':', '')
        if not datestring:
            raise ValueError("Empty string")
        tokens = _Tokenizer(datestring)
        if settings.DATE_ORDER:
            order = _resolve_date_order(settings.DATE_ORDER)
        else:
            order = cls._default_order
            if EIGHT_DIGIT.match(datestring):
                dt = cls._find_best_matching_date(datestring)
                if dt is not None:
                    return dt
        nsp = cls()
        ambiguous_date = None
        for token, _ in tokens.tokenize():
            for fmt in nsp.date_formats[order]:
                try:
                    dt = strptime(token, fmt), cls._get_period(fmt)
                    if len(str(dt[0].year)) < 4:
                        ambiguous_date = dt
                        continue
                    return dt
                except:
                    pass
        else:
            if ambiguous_date:
                return ambiguous_date
            else:
                raise ValueError('Unable to parse date from: %s' % datestring)
