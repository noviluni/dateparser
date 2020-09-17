from dateparser import date_parser


def parse_absolute_time(
    locale, date_string, translated_date_string, translated_date_string_with_formatting, date_formats, settings
):
    _order = settings.DATE_ORDER
    try:
        if settings.PREFER_LOCALE_DATE_ORDER:
            if 'DATE_ORDER' not in settings._mod_settings:
                settings.DATE_ORDER = locale.info.get('date_order', _order)
        date_obj, period = date_parser.parse(translated_date_string, settings=settings)
        settings.DATE_ORDER = _order
        return {
            'date_obj': date_obj,
            'period': period,
        }
    except ValueError:
        settings.DATE_ORDER = _order
        return None
