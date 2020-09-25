from datetime import datetime

import dateparser

# date_format = 'xxxx %B'
#
# print(dateparser.parse('xxxx junio', languages=['es'], date_formats=[date_format]))
# print(dateparser.parse('xxxx junio', languages=['en'], date_formats=[date_format]))
# print(dateparser.parse('xxxx junio', languages=['de'], date_formats=[date_format]))
#
# print(dateparser.parse('xxxx june', languages=['es'], date_formats=[date_format]))
# print(dateparser.parse('xxxx june', languages=['en'], date_formats=[date_format]))
# print(dateparser.parse('xxxx june', languages=['de'], date_formats=[date_format]))
#
# print(dateparser.parse('xxxx märz', languages=['es'], date_formats=[date_format]))
# print(dateparser.parse('xxxx märz', languages=['en'], date_formats=[date_format]))
# print(dateparser.parse('xxxx märz', languages=['de'], date_formats=[date_format]))


print(dateparser.parse('-3739996800000'))
print(dateparser.parse('-3739996800000') == datetime(1851, 6, 27, 0, 0))
# print(dateparser.parse('-186454800000'))
print(dateparser.parse('-1861945262080'))
print(dateparser.parse('-386380800'))
