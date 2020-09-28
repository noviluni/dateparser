# TODO: Add deprecation warning to the whole file

from dateparser.parsers import _resolve_date_order, _TimeParser
from dateparser.parsers.absolute_time_parser import \
    MICROSECOND as _MICROSECOND, HOUR_MINUTE_REGEX as _HOUR_MINUTE_REGEX, \
    MERIDIAN as _MERIDIAN, _get_unresolved_attrs
from dateparser.parsers.no_spaces_time_parser import \
    EIGHT_DIGIT as _EIGHT_DIGIT, \
    NSP_COMPATIBLE as _NSP_COMPATIBLE, _no_space_parser_eligibile
from dateparser.utils.string import _Tokenizer


NSP_COMPATIBLE = _NSP_COMPATIBLE  # TODO: add deprecation warning
MERIDIAN = _MERIDIAN  # TODO: add deprecation warning
MICROSECOND = _MICROSECOND  # TODO: add deprecation warning
EIGHT_DIGIT = _EIGHT_DIGIT  # TODO: add deprecation warning
HOUR_MINUTE_REGEX = _HOUR_MINUTE_REGEX  # TODO: add deprecation warning


def no_space_parser_eligibile(datestring):
    # TODO: add deprecation warning
    return _no_space_parser_eligibile(datestring)


def get_unresolved_attrs(parser_object):
    # TODO: add deprecation warning
    return _get_unresolved_attrs(parser_object)


def resolve_date_order(order, lst=None):
    # TODO: add deprecation warning
    return _resolve_date_order(order, lst)


time_parser = _TimeParser()  # TODO: add deprecation warning


class tokenizer(_Tokenizer):
    # TODO: add deprecation warning
    pass
