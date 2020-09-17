from dateparser.parsers.absolute_time import parse_absolute_time
from dateparser.parsers.custom_formats import parse_custom_formats
from dateparser.parsers.relative_time import parse_relative_time
from dateparser.parsers.timestamp import parse_timestamp

existing_parsers = {  # rename somehow to be easier to use
    'timestamp': parse_timestamp,
    'relative-time': parse_relative_time,
    'custom-formats': parse_custom_formats,  # move to first position?
    'absolute-time': parse_absolute_time,
}
