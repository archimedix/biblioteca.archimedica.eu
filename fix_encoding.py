#!/usr/bin/env python3
"""
Fix encoding issues in text - convert everything to proper UTF-8
"""

import html
import re

def fix_encoding(text):
    """
    Fix common encoding issues and convert to proper UTF-8
    """
    if not text:
        return text

    # First, decode HTML entities
    text = html.unescape(text)

    # Fix common mojibake (double-encoded UTF-8)
    # Order matters! More specific/longer patterns first
    replacements = [
        # Common Italian words (most specific first)
        ('piÃ¹', 'più'),
        ('perchÃ©', 'perché'),
        ('sarÃ ', 'sarà'),
        ('sarÃ', 'sarà'),  # without space
        ('verrÃ ', 'verrà'),
        ('verrÃ', 'verrà'),  # without space
        ('lÃ¬', 'lì'),
        ('cosÃ¬', 'così'),
        ('giÃ ', 'già'),
        ('giÃ', 'già'),  # without space
        ('quÃ¬', 'qui'),
        ('qualitÃ ', 'qualità'),
        ('qualitÃ', 'qualità'),  # without space
        ('cittÃ ', 'città'),
        ('cittÃ', 'città'),  # without space
        ('universitÃ ', 'università'),
        ('universitÃ', 'università'),  # without space
        ('novitÃ ', 'novità'),
        ('novitÃ', 'novità'),  # without space
        ('possibilitÃ ', 'possibilità'),
        ('possibilitÃ', 'possibilità'),  # without space
        ('attivitÃ ', 'attività'),
        ('attivitÃ', 'attività'),  # without space
        ('identitÃ ', 'identità'),
        ('identitÃ', 'identità'),  # without space
        ('libertÃ ', 'libertà'),
        ('libertÃ', 'libertà'),  # without space
        ('capacitÃ ', 'capacità'),
        ('capacitÃ', 'capacità'),  # without space
        ('visibilitÃ ', 'visibilità'),
        ('visibilitÃ', 'visibilità'),  # without space
        ('facoltÃ ', 'facoltà'),
        ('facoltÃ', 'facoltà'),  # without space
        ('originalitÃ ', 'originalità'),
        ('originalitÃ', 'originalità'),  # without space
        ('capillaritÃ ', 'capillarità'),
        ('capillaritÃ', 'capillarità'),  # without space

        # Special apostrophe combinations (before individual characters)
        ("câ€™Ã¨", "c'è"),
        ("lâ€™Ã¨", "l'è"),
        ("câ€™", "c'"),
        ("lâ€™", "l'"),
        ("dellâ€™", "dell'"),
        ("allâ€™", "all'"),
        ("sullâ€™", "sull'"),
        ("unâ€™", "un'"),
        ("nellâ€™", "nell'"),
        ("quellâ€™", "quell'"),
        ("dâ€™", "d'"),
        ("tuttiâ€™", "tutti'"),
        ("alâ€™", "al'"),
        ("dall'", "dall'"),

        # Quotes and apostrophes (smart quotes broken)
        ('â€™', "'"),
        ('â€˜', "'"),
        ('â€œ', '"'),
        ('â€', '"'),
        ('â€"', '—'),  # em dash
        ('â€"', '–'),  # en dash
        (''', "'"),
        (''', "'"),
        ('"', '"'),
        ('"', '"'),
        ('‚', ','),
        ('„', '"'),
        ('…', '...'),

        # Common Italian characters (individual)
        ('Ã¨', 'è'),
        ('Ã©', 'é'),
        ('Ãˆ', 'È'),
        ('Ã‰', 'É'),
        ('Ã ', 'à'),
        ('Ã¡', 'á'),
        ('Ã€', 'À'),
        ('Ã¬', 'ì'),
        ('Ã­', 'í'),
        ('ÃŒ', 'Ì'),
        ('Ã²', 'ò'),
        ('Ã³', 'ó'),
        ('Ã¹', 'ù'),
        ('Ãº', 'ú'),
        ('Ã™', 'Ù'),
        ('Ãš', 'Ú'),
        ('Ã§', 'ç'),
        ('Ã‡', 'Ç'),

        # Non-breaking space and other special spaces
        ('Â ', ' '),
        ('Â', ''),
        ('\xa0', ' '),

        # Encoding artifacts
        ('Ã‚', ''),
        ('â€ž', '"'),
        ('â€¦', '...'),
        ('â‚¬', '€'),
    ]

    # Apply replacements in order
    for old, new in replacements:
        text = text.replace(old, new)

    # Clean up multiple spaces
    text = re.sub(r'\s+', ' ', text)

    # Clean up spaces before punctuation
    text = re.sub(r'\s+([.,;:!?])', r'\1', text)

    return text.strip()

def test_fix_encoding():
    """Test the encoding fix function"""
    test_cases = [
        ("piÃ¹ interessante", "più interessante"),
        ("câ€™Ã¨ un problema", "c'è un problema"),
        ("lâ€™autore", "l'autore"),
        ("VenerdÃ¬ 14 Marzo", "Venerdì 14 Marzo"),
        ("Ã¨ davvero", "è davvero"),
        ("perchÃ©", "perché"),
        ("&#8217;", "'"),
        ("&nbsp;", " "),
    ]

    print("Testing encoding fixes:\n")
    all_passed = True
    for original, expected in test_cases:
        result = fix_encoding(original)
        passed = result == expected
        all_passed = all_passed and passed
        status = "✓" if passed else "✗"
        print(f"{status} '{original}' → '{result}' (expected: '{expected}')")

    print(f"\n{'All tests passed!' if all_passed else 'Some tests failed'}")
    return all_passed

if __name__ == '__main__':
    test_fix_encoding()
