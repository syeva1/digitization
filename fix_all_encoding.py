# -*- coding: utf-8 -*-
"""Phase 1: Fix encoding (Type B / invalid UTF-8 / UTF-8 mojibake) then apply Type A (CHAR_MAP + context) to all listed .txt."""
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
EXCLUDE = {'encoding_restoration_report.txt'}

# Type B: CP1251 bytes read as Latin-1
MOJIBARE_CP1251 = ('ãî', 'ñî', 'ðî', 'äóõ', 'îáù', 'ñîöè', 'ôîðì', 'êóëüò', 'æèçí', 'ñòâî', 'ìåæäó', 'áûëî', '÷òîáû')
# UTF-8 bytes read as Latin-1 (Ð³ = г, etc.)
MOJIBARE_UTF8 = ('Ð³', 'Ð¾', 'Ð´', 'Ð½', 'Ð¡', 'Ð ', 'ÐÐ')

def has_mojibake_cp1251(text):
    return any(p in text for p in MOJIBARE_CP1251)

def has_mojibake_utf8(text):
    return any(p in text for p in MOJIBARE_UTF8)

def try_cp1251(raw):
    try:
        return raw.decode('cp1251')
    except Exception:
        return None

def try_latin1_to_cp1251(text):
    try:
        return text.encode('latin-1').decode('cp1251')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return None

def try_latin1_to_utf8(text):
    try:
        return text.encode('latin-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return None

def main():
    list_path = os.path.join(BASE, 'encoding_fix_full_list.txt')
    if not os.path.exists(list_path):
        list_path = os.path.join(BASE, 'encoding_type_a_files.txt')
    if not os.path.exists(list_path):
        print('Run detect_encoding.py first, then create encoding_fix_full_list.txt (or use encoding_type_a_files.txt)')
        return 1

    with open(list_path, 'r', encoding='utf-8') as f:
        rel_paths = [line.strip() for line in f if line.strip()]
    rel_paths = [r for r in rel_paths if os.path.basename(r) not in EXCLUDE and r not in EXCLUDE]

    sys.path.insert(0, BASE)
    from fix_type_a import apply_map, apply_context_fixes

    fixed_encoding = 0
    fixed_a = 0
    errs = []

    for rel in rel_paths:
        path = os.path.join(BASE, rel)
        if not os.path.isfile(path):
            errs.append((rel, 'not found'))
            continue

        with open(path, 'rb') as f:
            raw = f.read()

        text = None
        try:
            text = raw.decode('utf-8')
        except UnicodeDecodeError:
            pass

        if text is None:
            text = try_cp1251(raw)
            if text is None:
                try:
                    text = raw.decode('cp1251', errors='replace')
                except Exception:
                    errs.append((rel, 'decode failed'))
                    continue
            fixed_encoding += 1
            print('Encoding (raw cp1251):', rel)

        else:
            # Valid UTF-8: fix mojibake if present
            if has_mojibake_utf8(text):
                out = try_latin1_to_utf8(text)
                if out is not None:
                    text = out
                    fixed_encoding += 1
                    print('Encoding (latin-1→utf-8):', rel)
            if has_mojibake_cp1251(text):
                out = try_latin1_to_cp1251(text)
                if out is not None:
                    text = out
                    fixed_encoding += 1
                    print('Encoding (latin-1→cp1251):', rel)

        before_a = text
        text = apply_map(text)
        text = apply_context_fixes(text)
        if text != before_a:
            fixed_a += 1
            print('Type A:', rel)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)

    print('Done. Encoding fixed:', fixed_encoding, '| Type A fixed:', fixed_a, '| Total processed:', len(rel_paths))
    for r, e in errs[:20]:
        print('  Error', r, e)
    return 0 if not errs else 1

if __name__ == '__main__':
    sys.exit(main())
