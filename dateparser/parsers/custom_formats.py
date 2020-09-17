from datetime import datetime

from dateparser.utils import set_correct_day_from_settings, \
    apply_timezone_from_settings


def parse_custom_formats(
    locale, date_string, translated_date_string, translated_date_string_with_formatting, date_formats, settings
):
    if not date_formats:
        return

    return parse_with_formats(
        translated_date_string_with_formatting,  # should this be "date_string" and use the locale?
        date_formats, settings=settings
    )


def parse_with_formats(date_string, date_formats, settings):
    """ Parse with formats and return a dictionary with 'period' and 'obj_date'.

    :returns: :class:`datetime.datetime`, dict or None

    """
    period = 'day'
    for date_format in date_formats:
        try:
            date_obj = datetime.strptime(date_string, date_format)
        except ValueError:
            continue
        else:
            if '%d' not in date_format:
                period = 'month'
                date_obj = set_correct_day_from_settings(date_obj, settings)

            if not ('%y' in date_format or '%Y' in date_format):
                today = datetime.today()
                date_obj = date_obj.replace(year=today.year)

            date_obj = apply_timezone_from_settings(date_obj, settings)

            return {'date_obj': date_obj, 'period': period}
    else:
        return {'date_obj': None, 'period': period}
