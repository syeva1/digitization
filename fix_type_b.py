# -*- coding: utf-8 -*-
"""Restore Type B files: CP1251 -> UTF-8 or fix double encoding (UTF-8 from Latin-1 misinterpretation)."""
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))

# Mojibake patterns that indicate CP1251 bytes were read as Latin-1
MOJIBARE = ('ãî', 'ñî', 'ðî', 'äóõ', 'îáù', 'ñîöè', 'ôîðì', 'êóëüò', 'æèçí', 'ñòâî', 'ìåæäó', 'áûëî', '÷òîáû')

def has_mojibake(text):
    return any(p in text for p in MOJIBARE)

def try_cp1251(raw):
    try:
        return raw.decode('cp1251')
    except Exception:
        return None

def try_latin1_roundtrip(text):
    """If text is UTF-8 but content is CP1251 misinterpreted as Latin-1, fix by encode latin-1 then decode cp1251."""
    try:
        return text.encode('latin-1').decode('cp1251')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return None

def main():
    list_path = os.path.join(BASE, 'encoding_type_b_files.txt')
    if not os.path.exists(list_path):
        print('Run detect_encoding.py first')
        return 1
    with open(list_path, 'r', encoding='utf-8') as f:
        rel_paths = [line.strip() for line in f if line.strip()]
    fixed_raw = 0
    fixed_roundtrip = 0
    skipped = 0
    errs = []
    for rel in rel_paths:
        path = os.path.join(BASE, rel)
        if not os.path.isfile(path):
            errs.append((rel, 'not found'))
            continue
        with open(path, 'rb') as f:
            raw = f.read()
        # Try 1: invalid UTF-8 -> decode as CP1251
        try:
            text_utf8 = raw.decode('utf-8')
        except UnicodeDecodeError:
            text_utf8 = None
        if text_utf8 is None:
            out = try_cp1251(raw)
            if out is not None:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(out)
                fixed_raw += 1
                print('Fixed (raw cp1251):', rel)
            else:
                errs.append((rel, 'decode failed'))
            continue
        # Valid UTF-8: check for mojibake
        if not has_mojibake(text_utf8):
            skipped += 1
            continue
        out = try_latin1_roundtrip(text_utf8)
        if out is not None:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(out)
            fixed_roundtrip += 1
            print('Fixed (latin-1 roundtrip):', rel)
        else:
            skipped += 1
    print('Type B: processed', len(rel_paths), '| fixed raw cp1251:', fixed_raw, '| fixed roundtrip:', fixed_roundtrip, '| skipped:', skipped)
    for r, e in errs[:15]:
        print('  Error', r, e)
    return 0

if __name__ == '__main__':
    sys.exit(main())
