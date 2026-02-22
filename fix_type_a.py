# -*- coding: utf-8 -*-
"""Restore Type A files: apply same character map as Gurova + optional context fixes."""
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))

# Same table as used for Gurova (wrong -> correct)
CHAR_MAP = {
    '\u040a': '\u041c',   # Њ -> М
    '\u040b': '\u041e',   # Ћ -> О
    '\u0403': '\u0413',   # Ѓ -> Г
    '\u0453': '\u0433',   # ѓ -> г
    '\u040f': '\u041f',   # Џ -> П
    '\u040c': '\u041d',   # Ќ -> Н
    '\u201a': '\u0412',   # ‚ -> В
    '\u0409': '\u041b',   # Љ -> Л
    '\u2039': '\u041a',   # ‹ -> К
    '\u0402': '\u0410',   # Ђ -> А
    '\u201e': '\u0414',   # „ -> Д
    '\u2026': '\u0415',   # … -> Е
    '\u20ac': '\u0418',   # € -> И
    '\ufffd': '\u0417',   # -> З
    '\u201c': '\u0424',   # " -> Ф
    '\u040e': '\u0423',   # Ў -> У
    '\u2014': '\u0427',   # — -> Ч
    '\u2020': '\u0416',   # † -> Ж
    '\u2019': '\u0422',   # ' -> Т
    '\u2018': '\u0421',   # ' -> С
    '\u2021': '\u0417',   # ‡ -> З
    '\u0452': '\u0434',   # ђ -> д
    '\u045b': '\u0441',   # ћ -> с
    '\u045a': '\u043d',   # њ -> н
    '\u045c': '\u044d',   # ќ -> э
    '\u045f': '\u044f',   # џ -> я
    '\u2022': '\u0419',   # • -> Й
    '\u203a': '\u0432',   # › -> в
}

def apply_map(text):
    for wrong, right in CHAR_MAP.items():
        text = text.replace(wrong, right)
    # Ь -> № only in " . Ь N" pattern (journal/number)
    text = text.replace('. \u042c ', '. \u2116 ')  # . Ь -> . №
    # " Р " -> " — " (space R space -> em dash)
    text = text.replace(' \u0420 ', ' \u2014 ')
    return text

def apply_context_fixes(text):
    """Optional context fixes that are safe for most Russian texts."""
    # Only apply if pattern exists
    if 'В\n ных' in text:
        text = text.replace('В\n ных', 'Из разных')
    if 'Сендерн' in text:
        text = text.replace('Сендерн', 'Гендерн')
    for old, new in [
        ('доссия', 'Россия'), ('доссии', 'России'), ('доссийскаЯ', 'российская'),
        ('доссиЯне', 'россияне'), ('доссийский', 'российский'), ('даботающие', 'Работающие'),
        ('дазличиЯ', 'Различия'), ('Гогатые', 'Богатые'), ('дедактор', 'Редактор'),
        ('деклама', 'Реклама'), ('Кидерами', 'Лидерами'), ('Кюди', 'Люди'),
        ('Логда ', 'Когда '), ('Лак известно', 'Как известно'), ('Лакие ', 'Какие '),
        ('Л ним ', 'К ним '), ('Лак заметила', 'Как заметила'), ('Лроме того', 'Кроме того'),
        ('ГританскаЯ', 'Британская'), ('ќлизабет', 'Элизабет'), ('ќндрю', 'Эндрю'),
        ('ќклектика', 'Эклектика'), ('ќти характеристики', 'Эти характеристики'),
        ('Фход от', 'Исход от'), ('дечь идет', 'Речь идет'),
        # Ганжа и др.: после замен џ->я, •->Й, ›->в
        ('Зйорошо', 'Хорошо'), ('ЗЙорошо', 'Хорошо'), ('ОГ ОСОГЕННОСТяЙ', 'ОС ОСОБЕННОСТЕЙ'), ('ОСОГЕННОСТяЙ', 'ОСОБЕННОСТЕЙ'),
        ('ПФГКИЧНвЙ ПдОСТдАНСТВ', 'ПРОСТРАНСТВ В'), ('ПдОСТдАНСТВ', 'ПРОСТРАНСТВ'), ('гОдОДЕ МОСЛВЕ', 'ГОРОДЕ МОСКВЕ'), ('В гОдОДЕ МОСЛВЕ', 'В ГОРОДЕ МОСКВЕ'),
        ('ОдМИдОВАНИя', 'ОСВЕДОМЛЕНИЯ'), ('ОПдОСв организации', 'ОПРОС организации'), ('диторика', 'риторика'), ('дичард', 'Ричард'),
        ('Ломмуницирующий', 'Коммуницирующий'), ('Лупол', 'Купол'), ('Флица', 'Улица'), ('Кичный', 'Личный'),
        # Колхас заголовок
        ('гИгАНТИЗМ, ИКИ ПдОГКЕМА ГОКнЗОгО', 'ГИГАНТИЗМ, ИЛИ ПРОБЛЕМА БОЛЬШОГО'),
        # Иванова / хлебные крошки
        ('ИНТЕКдОС > Ь33', 'ИНТЕКС > №33'), ('ИНТЕКдОС', 'ИНТЕКС'),
        ('ВерсиЯ', 'Версия'), (' длЯ ', ' для '),
        ('аналитической репреЙ', 'аналитической репрезентации'),
        # по смыслу: типичные опечатки
        ('интерпритация', 'интерпретация'), ('интерпритации', 'интерпретации'),
    ]:
        text = text.replace(old, new)
    return text

def main():
    list_path = os.path.join(BASE, 'encoding_type_a_files.txt')
    if not os.path.exists(list_path):
        print('Run detect_encoding.py first')
        return 1
    with open(list_path, 'r', encoding='utf-8') as f:
        rel_paths = [line.strip() for line in f if line.strip()]
    fixed = 0
    errs = []
    for rel in rel_paths:
        path = os.path.join(BASE, rel)
        if not os.path.isfile(path):
            errs.append((rel, 'not found'))
            continue
        try:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            errs.append((rel, str(e)))
            continue
        out = apply_map(text)
        out = apply_context_fixes(out)
        if out != text:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(out)
            fixed += 1
            print('Fixed:', rel)
    print('Total Type A processed:', len(rel_paths), '| Written:', fixed)
    for r, e in errs[:20]:
        print('  Error', r, e)
    return 0

if __name__ == '__main__':
    sys.exit(main())
