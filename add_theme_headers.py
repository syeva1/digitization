# -*- coding: utf-8 -*-
"""
Add "Тема / Источник / Содержание" block at the start of each .txt if not already present.
Run from repo root.
"""
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
EXCLUDE_DIRS = {'.git', '__pycache__'}
SKIP_FILES = {'full_txt_list_etalon.txt'}

RE_HAS_THEME = re.compile(r'^(#\s*)?Тема\s*:', re.M)


def path_to_theme_source(path_rel):
    """From path like 'Fundamentals of Sociology/Литература_классика/Moscow_Durkheim_Rules.txt'
    derive theme (parent folder) and source (filename)."""
    parts = path_rel.replace('\\', '/').split('/')
    if len(parts) >= 2:
        theme = parts[-2]
    else:
        theme = parts[0] if parts else ''
    name = parts[-1] if parts else ''
    source = name[:-4] if name.endswith('.txt') else name
    source = source.replace('_', ' ').strip()
    return theme, source


def build_header(path_rel):
    theme, source = path_to_theme_source(path_rel)
    return (
        "# Тема: {}\n"
        "# Источник: {}\n"
        "# Содержание: Материал курса. Подробнее — в README папки или по названию файла.\n\n"
    ).format(theme, source)


def process_file(path):
    rel = os.path.relpath(path, BASE)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        return False, str(e)
    if RE_HAS_THEME.search(text[:800]):
        return True, 0
    header = build_header(rel)
    new_text = header + text
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
    print('Done. Files with theme block added:', total)
    for rel, err in errors[:20]:
        print('Error', rel, err, file=__import__('sys').stderr)
    return 0 if not errors else 1


if __name__ == '__main__':
    exit(main())
