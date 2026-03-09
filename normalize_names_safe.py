# -*- coding: utf-8 -*-
"""
Safe renames: remove " — копия" from .txt filenames only when target does not exist.
Run from repo root. No folder renames.
"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
EXCLUDE_DIRS = {'.git', '__pycache__'}
SUFFIXES = (' — копия.txt', ' копия.txt')


def main():
    renames = []
    for root, dirs, filenames in os.walk(BASE):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for name in filenames:
            if not name.endswith('.txt'):
                continue
            suf = None
            for s in SUFFIXES:
                if name.endswith(s):
                    suf = s
                    break
            if not suf:
                continue
            new_name = name[:-len(suf)] + '.txt'
            path = os.path.join(root, name)
            target = os.path.join(root, new_name)
            if os.path.exists(target):
                continue
            try:
                os.rename(path, target)
                renames.append((path, target))
                print('Renamed:', os.path.relpath(path, BASE), '->', new_name)
            except Exception as e:
                print('Error', path, e, file=__import__('sys').stderr)
    print('Done. Renamed', len(renames), 'file(s).')
    return 0


if __name__ == '__main__':
    exit(main())
