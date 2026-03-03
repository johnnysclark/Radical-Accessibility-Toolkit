# -*- coding: utf-8 -*-
"""
Braille Translation Module  v1.0
=================================
Converts ASCII text to Unicode Braille (U+2800-U+28FF).

Grade 1 (uncontracted) is built-in using Python stdlib only.
Grade 2 (contracted) is available when liblouis is installed.

Handles capital indicators, number indicators, and common
punctuation per BANA (Braille Authority of North America) rules.

Part of the Radical Accessibility Project — UIUC School of Architecture.
Zero external dependencies.
"""

# ---------------------------------------------------------------------------
# Unicode Braille indicators
# ---------------------------------------------------------------------------

CAPITAL = '\u2820'       # dots 6        — next letter is uppercase
CAPITAL_WORD = '\u2820\u2820'  # double capital — entire word uppercase
NUMBER = '\u283c'        # dots 3456     — number indicator
LETTER_FOLLOWS = '\u2830'  # dots 56     — terminates number mode

# ---------------------------------------------------------------------------
# Grade 1: letter-by-letter ASCII → Unicode Braille
# ---------------------------------------------------------------------------

_LETTERS = {
    'a': '\u2801', 'b': '\u2803', 'c': '\u2809', 'd': '\u2819',
    'e': '\u2811', 'f': '\u280b', 'g': '\u281b', 'h': '\u2813',
    'i': '\u280a', 'j': '\u281a', 'k': '\u2805', 'l': '\u2807',
    'm': '\u280d', 'n': '\u281d', 'o': '\u2815', 'p': '\u280f',
    'q': '\u281f', 'r': '\u2817', 's': '\u280e', 't': '\u281e',
    'u': '\u2825', 'v': '\u2827', 'w': '\u283a', 'x': '\u282d',
    'y': '\u283d', 'z': '\u2835',
}

# Digits share dot patterns with letters a-j, preceded by NUMBER indicator
_DIGITS = {
    '1': '\u2801', '2': '\u2803', '3': '\u2809', '4': '\u2819',
    '5': '\u2811', '6': '\u280b', '7': '\u281b', '8': '\u2813',
    '9': '\u280a', '0': '\u281a',
}

_PUNCTUATION = {
    ' ':  ' ',
    '.':  '\u2832',   # dots 256
    ',':  '\u2802',   # dot 2
    '?':  '\u2826',   # dots 236
    '!':  '\u2816',   # dots 235
    '-':  '\u2824',   # dots 36
    "'":  '\u2804',   # dot 3
    ':':  '\u2812',   # dots 25
    ';':  '\u2806',   # dots 23
    '/':  '\u280c',   # dots 34
    '(':  '\u2836',   # dots 2356
    ')':  '\u2836',   # dots 2356
    '"':  '\u2826',   # opening/closing — simplified
    '#':  '\u283c',   # number sign
    '&':  '\u282f',   # dots 12346
    '@':  '\u2800',   # placeholder — rarely used in arch labels
    '+':  '\u2816',   # dots 235
    '=':  '\u2836',   # dots 2356
    '*':  '\u2814',   # dots 35
    '%':  '\u2825',   # simplified
    '_':  '\u2824',   # treated as dash
    '\n': ' ',        # newline → space
    '\t': ' ',        # tab → space
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def to_braille(text, grade=1):
    """Convert text to Unicode Braille.

    Grade 1 (uncontracted) is built-in.
    Grade 2 (contracted) requires liblouis — falls back to Grade 1 if
    liblouis is not installed.

    Args:
        text:  Plain ASCII/Unicode text.
        grade: 1 for uncontracted, 2 for contracted.

    Returns:
        Unicode Braille string (U+2800-U+28FF range).
    """
    if not text:
        return ""
    if grade == 2:
        return to_braille_grade2(text)
    return _grade1(text)


def to_braille_grade2(text):
    """Try liblouis for Grade 2 contracted braille.

    Falls back to Grade 1 if liblouis is unavailable.
    """
    if not text:
        return ""
    try:
        import louis  # type: ignore
        mode = louis.dotsIO | louis.ucBrl
        result = louis.translate(["en-us-g2.ctb"], text, mode=mode)
        return result[0]
    except (ImportError, AttributeError, Exception):
        return _grade1(text)


def from_braille(braille_text):
    """Best-effort conversion of Unicode Braille back to ASCII.

    Handles letters and digits.  Does not reverse Grade 2 contractions.
    """
    if not braille_text:
        return ""

    # Build reverse maps
    rev_letters = {v: k for k, v in _LETTERS.items()}
    rev_digits = {v: k for k, v in _DIGITS.items()}

    result = []
    in_number = False
    next_cap = False

    for ch in braille_text:
        if ch == CAPITAL:
            next_cap = True
            continue
        if ch == NUMBER:
            in_number = True
            continue
        if ch == LETTER_FOLLOWS:
            in_number = False
            continue
        if ch == ' ':
            in_number = False
            result.append(' ')
            continue

        if in_number and ch in rev_digits:
            result.append(rev_digits[ch])
        elif ch in rev_letters:
            letter = rev_letters[ch]
            if next_cap:
                letter = letter.upper()
                next_cap = False
            result.append(letter)
        else:
            # Try punctuation reverse lookup
            rev_punct = {v: k for k, v in _PUNCTUATION.items()}
            result.append(rev_punct.get(ch, ch))

    return "".join(result)


def braille_len(braille_text):
    """Return the number of braille cells (visible characters) in a string.

    Spaces count as one cell.  Indicators (capital, number) also count.
    """
    return len(braille_text)


# ---------------------------------------------------------------------------
# Internal: Grade 1 converter
# ---------------------------------------------------------------------------

def _grade1(text):
    """Character-by-character Grade 1 braille translation."""
    result = []
    in_number = False

    for ch in text:
        # Space terminates number mode
        if ch == ' ':
            in_number = False
            result.append(' ')
            continue

        # Digit
        if ch in _DIGITS:
            if not in_number:
                result.append(NUMBER)
                in_number = True
            result.append(_DIGITS[ch])
            continue

        # Letter (terminates number mode)
        lower = ch.lower()
        if lower in _LETTERS:
            if in_number:
                result.append(LETTER_FOLLOWS)
                in_number = False
            if ch.isupper():
                result.append(CAPITAL)
            result.append(_LETTERS[lower])
            continue

        # Punctuation terminates number mode (except period/comma after digits)
        if ch in _PUNCTUATION:
            if in_number and ch not in ('.', ','):
                in_number = False
            result.append(_PUNCTUATION[ch])
            continue

        # Unknown character — pass through as-is
        in_number = False
        result.append(ch)

    return "".join(result)
