# -*- coding: utf-8 -*-
"""Apply fix_type_a (CHAR_MAP + context) to ALL .txt in Введение_академическое_письмо."""
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
VVEDENIE = os.path.join(BASE, "Академическое письмо", "Введение_академическое_письмо")

# Import logic from fix_type_a
sys.path.insert(0, BASE)
from fix_type_a import apply_map, apply_context_fixes

def main():
    fixed = 0
    for root, dirs, files in os.walk(VVEDENIE):
        for f in files:
            if not f.lower().endswith('.txt'):
                continue
            path = os.path.join(root, f)
            rel = os.path.relpath(path, BASE)
            try:
                with open(path, 'r', encoding='utf-8') as fp:
                    text = fp.read()
            except Exception as e:
                print('Error reading', rel, e)
                continue
            out = apply_map(text)
            out = apply_context_fixes(out)
            if out != text:
                with open(path, 'w', encoding='utf-8') as fp:
                    fp.write(out)
                fixed += 1
                print('Fixed:', rel)
    print('Done. Files fixed:', fixed)
    return 0

if __name__ == '__main__':
    sys.exit(main())
