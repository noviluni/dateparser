from dateparser.freshness_date_parser import freshness_date_parser


def parse_relative_time(
    locale, date_string, translated_date_string, translated_date_string_with_formatting, date_formats, settings
):
    try:
        return freshness_date_parser.get_date_data(translated_date_string, settings)
    except (OverflowError, ValueError):
        return None
