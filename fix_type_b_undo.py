# -*- coding: utf-8 -*-
"""Undo wrong Type B fix: file was UTF-8 but we decoded as CP1251 and saved.
   Recovery: read current (UTF-8), encode as cp1251 -> original bytes, decode as utf-8 -> correct text."""
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))

def undo_type_b(path):
    with open(path, 'r', encoding='utf-8') as f:
        current = f.read()
    try:
        raw = current.encode('cp1251')
        correct = raw.decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return False, "encode/decode error"
    with open(path, 'w', encoding='utf-8') as f:
        f.write(correct)
    return True, None

if __name__ == '__main__':
    rel = "Академическое письмо/Введение_академическое_письмо/Материалы для группы, которая работает автономно/Зиммель Г_Большие города и духовная жизнь/Зиммель Г_Большие города и духовная жизнь.txt"
    path = os.path.join(BASE, rel)
    if not os.path.isfile(path):
        print('File not found:', path)
        sys.exit(1)
    ok, err = undo_type_b(path)
    if ok:
        print('Fixed (undo Type B):', rel)
    else:
        print('Error:', err)
    sys.exit(0 if ok else 1)
