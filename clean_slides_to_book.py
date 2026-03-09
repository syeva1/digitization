# -*- coding: utf-8 -*-
"""
Clean .txt course materials: remove slide markers, export headers, PDF stamps,
and slide numbers so text reads as a continuous book. Run from repo root.
"""
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))

# Patterns
RE_SLIDE = re.compile(r'^=== (?:Slide|Слайд) \d+ ===\s*$')
RE_SLIDE_ANY = re.compile(r'=== (?:Slide|Слайд) \d+ ===')
RE_PDF_STAMP = re.compile(r'^PDF to Markdown[\t ].*\d{2}\.\d{2}\.\d{4}.*$')
RE_READY = re.compile(r'^ГОТОВО!\s*$')
RE_SLIDE_NUMBER = re.compile(r'^\d{1,2}\s*$')
RE_HEADER_LINE1 = re.compile(r'^Название документа:\s*.+$')
RE_HEADER_LINE2 = re.compile(r'^Автор/курс/дата:\s*.+$')
RE_HEADER_LINE3 = re.compile(r'^Общее количество слайдов:\s*\d+$')
RE_HEADER_LINE4 = re.compile(r'^[-]{4,}\s*$')
# Extended cleanup (plan: PAGE, Total slides, Footer, long dashes)
RE_PAGE = re.compile(r'^===== PAGE \d+ =====\s*$')
RE_TOTAL_SLIDES = re.compile(r'^Total slides/pages:\s*\d+\s*$')
RE_FOOTER = re.compile(r'^Footer:\s*$')
RE_LONG_DASH = re.compile(r'^[-]{20,}\s*$')

EXCLUDE_DIRS = {'.git', '__pycache__'}
EXCLUDE_FILES = {'encoding_fix_full_list.txt', 'encoding_type_a_files.txt', 'encoding_restoration_report.txt', 'full_txt_list_etalon.txt'}


def has_slide_markers(lines):
    return any(RE_SLIDE_ANY.search(line) for line in lines)


def remove_header_block(lines):
    """Remove 4-line header at start if present."""
    if len(lines) < 5:
        return lines
    if (RE_HEADER_LINE1.match(lines[0]) and
            RE_HEADER_LINE2.match(lines[1]) and
            RE_HEADER_LINE3.match(lines[2]) and
            RE_HEADER_LINE4.match(lines[3]) and
            lines[4].strip() == ''):
        return lines[5:]
    return lines


def _read_maybe_convert(path):
    """Read as UTF-8; on decode error try to convert to UTF-8 and save. Returns (text, None) or (None, error)."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read(), None
    except UnicodeDecodeError:
        pass
    for enc in ('cp1251', 'windows-1251', 'cp1252', 'latin-1', 'iso-8859-1'):
        try:
            with open(path, 'r', encoding=enc) as f:
                text = f.read()
            with open(path, 'w', encoding='utf-8') as f:
                f.write(text)
            return text, None
        except Exception:
            continue
    return None, 'Could not decode as UTF-8 or common encodings'


def clean_file(path, remove_standalone_dashes=False):
    text, err = _read_maybe_convert(path)
    if err:
        return False, err
    lines = text.splitlines(keepends=True) if text else []
    if not lines:
        return True, 0

    had_slides = has_slide_markers(lines)
    out = []
    i = 0
    n = len(lines)
    changes = 0

    # 1. Remove 4-line header at start
    if n >= 5:
        if (RE_HEADER_LINE1.match(lines[0].rstrip()) and
                RE_HEADER_LINE2.match(lines[1].rstrip()) and
                RE_HEADER_LINE3.match(lines[2].rstrip()) and
                RE_HEADER_LINE4.match(lines[3].rstrip()) and
                lines[4].strip() == ''):
            i = 5
            changes += 5

    while i < n:
        line = lines[i]
        stripped = line.rstrip()
        # 2. Remove === Slide N === / === Слайд N ===
        if RE_SLIDE.match(stripped):
            i += 1
            changes += 1
            continue
        # 3. Remove PDF to Markdown stamp
        if RE_PDF_STAMP.match(stripped):
            i += 1
            changes += 1
            # Skip following blank lines
            while i < n and lines[i].strip() == '':
                i += 1
                changes += 1
            continue
        # 4. Remove ГОТОВО!
        if RE_READY.match(stripped):
            i += 1
            changes += 1
            continue
        # 5. In slide files: remove standalone 1-2 digit line (slide number)
        if had_slides and RE_SLIDE_NUMBER.match(stripped):
            i += 1
            changes += 1
            continue
        # 6. Optional: remove standalone --- in slide files
        if remove_standalone_dashes and had_slides and stripped == '---':
            i += 1
            changes += 1
            continue
        # 7. ===== PAGE N =====
        if RE_PAGE.match(stripped):
            i += 1
            changes += 1
            continue
        # 8. Total slides/pages: N and optional following ---- line
        if RE_TOTAL_SLIDES.match(stripped):
            i += 1
            changes += 1
            if i < n and RE_LONG_DASH.match(lines[i].rstrip()):
                i += 1
                changes += 1
            continue
        # 9. Footer: + next line
        if RE_FOOTER.match(stripped):
            i += 1
            changes += 1
            if i < n:
                i += 1
                changes += 1
            continue
        # 10. Standalone long dash line (e.g. --------------------------------------------------)
        if RE_LONG_DASH.match(stripped):
            i += 1
            changes += 1
            continue
        out.append(line)
        i += 1
    if changes == 0:
        return True, 0
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(out)
    except Exception as e:
        return False, str(e)
    return True, changes


def main():
    only_with_slides = '--slides-only' in sys.argv
    remove_dashes = '--remove-dashes' in sys.argv
    dry_run = '--dry-run' in sys.argv
    process_all = '--all' in sys.argv
    total_files = 0
    total_changes = 0
    errors = []
    for root, dirs, filenames in os.walk(BASE):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for name in filenames:
            if not name.endswith('.txt'):
                continue
            if not process_all and (name in EXCLUDE_FILES or name.startswith('fix_') or name.startswith('encoding_')):
                continue
            if name == 'full_txt_list_etalon.txt':
                continue
            path = os.path.join(root, name)
            rel = os.path.relpath(path, BASE)
            if only_with_slides:
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        if '=== Slide' not in f.read() and '=== Слайд' not in f.read():
                            continue
                except Exception:
                    continue
            if dry_run:
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    if RE_SLIDE_ANY.search(content) or RE_PDF_STAMP.search(content) or RE_READY.search(content):
                        print('Would process:', rel)
                        total_files += 1
                except Exception as e:
                    errors.append((rel, str(e)))
                continue
            ok, result = clean_file(path, remove_standalone_dashes=remove_dashes)
            if not ok:
                errors.append((rel, result))
                continue
            if result > 0:
                total_files += 1
                total_changes += result
                print('Cleaned {} ({} lines removed)'.format(rel, result))
    if dry_run:
        print('Would process {} file(s)'.format(total_files))
    else:
        print('Done. Files modified: {}, total lines removed: {}'.format(total_files, total_changes))
    for rel, err in errors[:15]:
        print('Error {}: {}'.format(rel, err), file=sys.stderr)
    return 0 if not errors else 1


if __name__ == '__main__':
    sys.exit(main())
