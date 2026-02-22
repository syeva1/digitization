# -*- coding: utf-8 -*-
"""Detect Type A (wrong Cyrillic in UTF-8) and Type B (CP1251/Latin-1 mojibake) in .txt files."""
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))

# Type A: only Cyrillic wrong chars (Serbian/Macedonian) + џ, •, ›
TYPE_A_CYRILLIC = set(
    '\u040a\u040b\u0403\u0453\u040f\u040c\u0409\u2039\u0402\u201e\u201c\u040e'
    '\u2020\u2019\u2018\u2021\u0452\u045b\u045c\u045a'
    '\u045f\u2022\u203a'  # џ -> я, • -> Й, › -> в
)
# Plus typographic used as letters (only count if file also has Russian + one of above, or we use below)
TYPE_A_TYPO = set('\u201a\u2026\u20ac\u2014')  # ‚…€—
# Normal Cyrillic (Russian) - need at least some to consider file as Russian
RUSSIAN_CYRILLIC = set('абвгдежзийклмнопрстуфхцчшщъыьэюяАБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ')

# Type B: mojibake patterns (CP1251 bytes interpreted as Latin-1)
TYPE_B_MOJIBARE = ('ãî', 'ñî', 'ðî', 'äóõ', 'îáù', 'ñîöè', 'ôîðì', 'êóëüò', 'æèçí', 'ñòâî', 'ìåæäó', 'áûëî', '÷òîáû', 'íåîáõîäèìî', 'ïðèâîäèò')

def has_type_a(text):
    if not text or not RUSSIAN_CYRILLIC.intersection(text):
        return False
    # Must have wrong Cyrillic (ЊЋЃѓЏЌЉ‹Ђ etc.), not just € or … in English
    return bool(TYPE_A_CYRILLIC.intersection(text))

def has_type_b_mojibake(text):
    """UTF-8 string that looks like CP1251 decoded as Latin-1."""
    return any(p in text for p in TYPE_B_MOJIBARE)

def can_decode_cp1251(raw):
    try:
        s = raw.decode('cp1251')
        # Heuristic: has some Russian words
        return bool(RUSSIAN_CYRILLIC.intersection(s)) and (' ' in s or '\n' in s)
    except Exception:
        return False

def main():
    type_a_files = []
    type_b_files = []
    errors = []
    count = 0

    for root, dirs, files in os.walk(BASE):
        dirs[:] = [d for d in dirs if d != '.git']
        for f in files:
            if not f.lower().endswith('.txt'):
                continue
            path = os.path.join(root, f)
            rel = os.path.relpath(path, BASE)
            count += 1
            try:
                with open(path, 'rb') as fp:
                    raw = fp.read()
            except Exception as e:
                errors.append((rel, str(e)))
                continue

            # Try UTF-8 first
            try:
                text = raw.decode('utf-8')
            except UnicodeDecodeError:
                text = None

            if text is not None:
                if has_type_a(text):
                    type_a_files.append(rel)
                if has_type_b_mojibake(text):
                    type_b_files.append(rel)
                # Also check: file might be valid UTF-8 but actually CP1251 bytes mis-saved
                # (then it would have given decode error or replacement chars)
            else:
                # Invalid UTF-8: maybe raw CP1251?
                if can_decode_cp1251(raw):
                    type_b_files.append(rel)
                # else leave as unclassified

    # Dedupe type_b (same file could be both; for B we only need once)
    type_b_files = list(dict.fromkeys(type_b_files))
    # Type A and B can overlap; keep both lists as-is for processing

    with open(os.path.join(BASE, 'encoding_type_a_files.txt'), 'w', encoding='utf-8') as out:
        for p in sorted(type_a_files):
            out.write(p + '\n')
    with open(os.path.join(BASE, 'encoding_type_b_files.txt'), 'w', encoding='utf-8') as out:
        for p in sorted(type_b_files):
            out.write(p + '\n')

    print('Scanned:', count, 'files')
    print('Type A (wrong Cyrillic):', len(type_a_files))
    for p in sorted(type_a_files):
        print('  ', p)
    print('Type B (CP1251/mojibake):', len(type_b_files))
    for p in sorted(type_b_files):
        print('  ', p)
    if errors:
        print('Errors:', len(errors))
        for r, e in errors[:10]:
            print('  ', r, e)
    return 0

if __name__ == '__main__':
    sys.exit(main())
