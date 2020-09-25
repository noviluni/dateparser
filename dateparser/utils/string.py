from io import StringIO

import regex as re

_APOSTROPHE_LOOK_ALIKE_CHARS = [
    '\N{RIGHT SINGLE QUOTATION MARK}',     # '\u2019'
    '\N{MODIFIER LETTER APOSTROPHE}',      # '\u02bc'
    '\N{MODIFIER LETTER TURNED COMMA}',    # '\u02bb'
    '\N{ARMENIAN APOSTROPHE}',             # '\u055a'
    '\N{LATIN SMALL LETTER SALTILLO}',     # '\ua78c'
    '\N{PRIME}',                           # '\u2032'
    '\N{REVERSED PRIME}',                  # '\u2035'
    '\N{MODIFIER LETTER PRIME}',           # '\u02b9'
    '\N{FULLWIDTH APOSTROPHE}',            # '\uff07'
]

_RE_NBSP = re.compile('\xa0', flags=re.UNICODE)
_RE_SPACES = re.compile(r'\s+')
_RE_TRIM_SPACES = re.compile(r'^\s+(\S.*?)\s+$')
_RE_TRIM_COLONS = re.compile(r'(\S.*?):*$')

_RE_SANITIZE_SKIP = re.compile(r'\t|\n|\r|\u00bb|,\s\u0432|\u200e|\xb7|\u200f|\u064e|\u064f', flags=re.M)
_RE_SANITIZE_RUSSIAN = re.compile(r'([\W\d])\u0433\.', flags=re.I | re.U)
_RE_SANITIZE_PERIOD = re.compile(r'(?<=\D+)\.', flags=re.U)
_RE_SANITIZE_ON = re.compile(r'^.*?on:\s+(.*)')
_RE_SANITIZE_APOSTROPHE = re.compile('|'.join(_APOSTROPHE_LOOK_ALIKE_CHARS))


def sanitize_spaces(date_string):
    date_string = _RE_NBSP.sub(' ', date_string)
    date_string = _RE_SPACES.sub(' ', date_string)
    date_string = _RE_TRIM_SPACES.sub(r'\1', date_string)
    return date_string


def sanitize_date(date_string):
    date_string = _RE_SANITIZE_SKIP.sub(' ', date_string)
    date_string = _RE_SANITIZE_RUSSIAN.sub(r'\1 ', date_string)  # remove 'г.' (Russian for year) but not in words
    date_string = sanitize_spaces(date_string)
    date_string = _RE_SANITIZE_PERIOD.sub('', date_string)
    date_string = _RE_SANITIZE_ON.sub(r'\1', date_string)
    date_string = _RE_TRIM_COLONS.sub(r'\1', date_string)

    date_string = _RE_SANITIZE_APOSTROPHE.sub("'", date_string)

    return date_string


class _Tokenizer:
    digits = '0123456789:'
    letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

    def _isletter(self, tkn):
        return tkn in self.letters

    def _isdigit(self, tkn):
        return tkn in self.digits

    def __init__(self, ds):
        self.instream = StringIO(ds)

    def _switch(self, chara, charb):
        if self._isdigit(chara):
            return 0, not self._isdigit(charb)

        if self._isletter(chara):
            return 1, not self._isletter(charb)

        return 2, self._isdigit(charb) or self._isletter(charb)

    def tokenize(self):
        token = ''
        EOF = False

        while not EOF:
            nextchar = self.instream.read(1)

            if not nextchar:
                EOF = True
                type, _ = self._switch(token[-1], nextchar)
                yield token, type
                return

            if token:
                type, switch = self._switch(token[-1], nextchar)

                if not switch:
                    token += nextchar
                else:
                    yield token, type
                    token = nextchar
            else:
                token += nextchar
