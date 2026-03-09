# -*- coding: utf-8 -*-
"""
Normalize title blocks (yy->by, ANSLATED->TRANSLATED, etc.) and remove
obvious OCR garbage: standalone page numbers and known fragment lines.
Run from repo root. Processes all .txt except full_txt_list_etalon.txt.
"""
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
EXCLUDE_DIRS = {'.git', '__pycache__'}
SKIP_FILES = {'full_txt_list_etalon.txt'}

# Title block fixes (apply to first ~50 lines)
TITLE_REPLACEMENTS = [
    (r'\byy\s+Emile\b', 'by Emile'),
    (r'\byy\s+', 'by '),
    (r'ANSLATED\b', 'TRANSLATED'),
    (r'\bITED\b', 'EDITED'),
]
# Remove lines that are just 1-3 chars / garbage in title area
RE_TITLE_GARBAGE_LINE = re.compile(r'^[A-Za-z]{1,2}[|\s]*$')  # Fp| etc.
RE_STANDALONE_PAGE = re.compile(r'^\d{2,4}\s*$')
# Known OCR fragment lines (exact match, strip)
OCR_FRAGMENTS = {
    'of |', 'nat', 'of z', 'sam', 'fror', 'it is', 'hen', 'tot', 'nam',
    'to tl', 'disc', 'ones', 'of |', 'of z',
}


def fix_title_block(text):
    lines = text.split('\n')
    changed = False
    out = []
    title_zone = min(50, len(lines))
    for i, line in enumerate(lines):
        if i < title_zone:
            new_line = line
            for pat, repl in TITLE_REPLACEMENTS:
                new_line = re.sub(pat, repl, new_line)
            if new_line != line:
                changed = True
                line = new_line
            if RE_TITLE_GARBAGE_LINE.match(line.strip()) and line.strip():
                changed = True
                continue
        out.append(line)
    return '\n'.join(out) if changed else None


def remove_ocr_garbage(text):
    lines = text.split('\n')
    out = []
    i = 0
    n = len(lines)
    changed = False
    while i < n:
        line = lines[i]
        stripped = line.strip()
        # Standalone page number (2-4 digits)
        if RE_STANDALONE_PAGE.match(stripped):
            i += 1
            changed = True
            continue
        # Known OCR fragment as whole line
        if stripped in OCR_FRAGMENTS:
            i += 1
            changed = True
            continue
        out.append(line)
        i += 1
    return '\n'.join(out) if changed else None


def process_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        return False, str(e)
    new_text = text
    titled = fix_title_block(new_text)
    if titled is not None:
        new_text = titled
    ocr = remove_ocr_garbage(new_text)
    if ocr is not None:
        new_text = ocr
    if new_text == text:
        return True, 0
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_text)
    except Exception as e:
        return False, str(e)
    return True, 1


def main():
    total = 0
    errors = []
    for root, dirs, filenames in os.walk(BASE):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for name in filenames:
            if not name.endswith('.txt') or name in SKIP_FILES:
                continue
            path = os.path.join(root, name)
            rel = os.path.relpath(path, BASE)
            ok, result = process_file(path)
            if not ok:
                errors.append((rel, result))
            elif result:
                total += 1
                print('Processed:', rel)
    print('Done. Files modified:', total)
    for rel, err in errors[:20]:
        print('Error', rel, err, file=__import__('sys').stderr)
    return 0 if not errors else 1


if __name__ == '__main__':
    exit(main())
