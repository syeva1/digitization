# -*- coding: utf-8 -*-
"""Remove junk lines from course .txt: URL-only lines, breadcrumbs with date, 'Вернуться назад', print:page + N/M."""
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
EXCLUDE_FILES = {
    'encoding_restoration_report.txt',
    'encoding_type_a_files.txt',
    'encoding_type_b_files.txt',
    'encoding_fix_full_list.txt',
}

# Line is only URL (starts with http/https/www, maybe trailing tab + N/M)
URL_START = re.compile(r'^\s*(https?://|HTTP://|www\.)', re.IGNORECASE)
# Line: optional "DD.MM.YYYY, HH:MM" + tab + "ИНТЕКС >" or "ИНТЕКдОС >"
BREADCRUMB = re.compile(
    r'^(\d{2}\.\d{2}\.\d{4},\s*\d{1,2}:\d{2})?\s*\t.*(ИНТЕКС\s*>\s*|ИНТЕКдОС\s*>\s*)',
    re.IGNORECASE
)
# Line contains print:page and ends with tab + N/M (page number)
PRINT_PAGE = re.compile(r'print:page.*\t\d+/\d+\s*$')

def is_junk_line(line):
    s = line.rstrip('\n\r')
    stripped = s.strip()
    if not stripped:
        return False  # empty: keep (or handle by collapse later)
    if stripped in ('ВернутьсЯ назад', 'Вернуться назад'):
        return True
    if URL_START.match(stripped):
        return True
    if BREADCRUMB.match(s):
        return True
    if PRINT_PAGE.search(s):
        return True
    return False

def process_file(path, dry_run=False, collapse_dupes=False, trim_trailing_blanks=2):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return 0, str(e)
    out = []
    prev = None
    removed = 0
    for line in lines:
        if is_junk_line(line):
            removed += 1
            if dry_run:
                print('  REMOVE:', repr(line[:80]))
            continue
        if collapse_dupes and line == prev and (not line.strip() or prev is not None):
            if line.strip():
                removed += 1
                if dry_run:
                    print('  DEDUP:', repr(line[:60]))
                continue
        out.append(line)
        prev = line
    # Trim excess trailing blank lines to at most one (if more than trim_trailing_blanks)
    if trim_trailing_blanks >= 1 and len(out) > 1:
        n = 0
        for i in range(len(out) - 1, -1, -1):
            if out[i].strip() != '':
                break
            n += 1
        if n > trim_trailing_blanks:
            del out[-(n - 1):]
            removed += n - 1
    if not dry_run and removed > 0:
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(out)
    return removed, None

def main():
    dry_run = '--dry-run' in sys.argv
    collapse_dupes = '--collapse-dupes' in sys.argv
    trim = 2
    if '--trim-trailing' in sys.argv:
        i = sys.argv.index('--trim-trailing')
        if i + 1 < len(sys.argv):
            try:
                trim = int(sys.argv[i + 1])
            except ValueError:
                pass

    total_files = 0
    total_removed = 0
    errors = []
    for root, dirs, files in os.walk(BASE):
        dirs[:] = [d for d in dirs if d != '.git']
        for f in files:
            if not f.lower().endswith('.txt'):
                continue
            if f in EXCLUDE_FILES:
                continue
            path = os.path.join(root, f)
            rel = os.path.relpath(path, BASE)
            removed, err = process_file(path, dry_run=dry_run, collapse_dupes=collapse_dupes, trim_trailing_blanks=trim)
            if err:
                errors.append((rel, err))
                continue
            if removed > 0:
                total_files += 1
                total_removed += removed
                if dry_run:
                    print(rel, ':', removed, 'lines')
                else:
                    print(rel, ':', removed, 'lines removed')
    if dry_run:
        print('Dry run. Would remove', total_removed, 'lines in', total_files, 'files.')
    else:
        print('Done. Removed', total_removed, 'lines in', total_files, 'files.')
    for rel, e in errors[:10]:
        print('Error', rel, e)
    return 0

if __name__ == '__main__':
    sys.exit(main())
