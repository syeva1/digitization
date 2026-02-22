# -*- coding: utf-8 -*-
"""Fix 12 specific files: Type B (mojibake CP1251) + Type A (wrong Cyrillic)."""
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))

# 12 files relative to BASE (Оцифровка)
FILES = [
    "Академическое письмо/Введение_академическое_письмо/Материалы для группы, которая работает автономно/001_Список текстов/001_Список текстов.txt",
    "Академическое письмо/Введение_академическое_письмо/Материалы для группы, которая работает автономно/Ганжа А_Mobilis in mobili/Ганжа А_Mobilis in mobili.txt",
    "Академическое письмо/Введение_академическое_письмо/Материалы для группы, которая работает автономно/Зиммель Г_Большие города и духовная жизнь/Зиммель Г_Большие города и духовная жизнь.txt",
    "Академическое письмо/Введение_академическое_письмо/Материалы для группы, которая работает автономно/Иванова А_Танцующие пассажиры/Иванова А_Танцующие пассажиры.txt",
    "Академическое письмо/Введение_академическое_письмо/Материалы для группы, которая работает автономно/Колхас Р_Гигантизм или проблема большого/Колхас Р_Гигантизм или проблема большого.txt",
    "Академическое письмо/Введение_академическое_письмо/Материалы для группы, которая работает автономно/Лотман Ю_Проблемы семиотики города/lotman_ocr.txt",
    "Академическое письмо/Введение_академическое_письмо/Материалы для группы, которая работает автономно/Рожков К_Маркетинговый подход к изучению мегаполиса/Рожков К_Маркетинговый подход к изучению мегаполиса.txt",
    "Академическое письмо/Введение_академическое_письмо/Материалы для группы, которая работает автономно/Рубл Б_Творческий потенциал контактных зон/Рубл Б_Творческий потенциал контактных зон.txt",
    "Академическое письмо/Введение_академическое_письмо/Материалы для группы, которая работает автономно/Сорокина Н_Субъективные маршруты/Сорокина Н_Субъективные маршруты.txt",
    "Академическое письмо/Введение_академическое_письмо/Материалы для группы, которая работает автономно/Трубина Е_Полис и мегасобытия 2/Трубина Е_Полис и мегасобытия.txt",
    "Академическое письмо/Введение_академическое_письмо/Материалы для группы, которая работает автономно/ЦИТАТЫ_2023/ЦИТАТЫ_2023.txt",
    "Академическое письмо/Введение_академическое_письмо/Материалы для группы, которая работает автономно/Ярская-Смирнова и др_Кидалт вы или обыкновенный человек/Ярская-Смирнова и др_Кидалт вы или обыкновенный человек.txt",
]

# CP1251 read as Latin-1 (ãî, ñî...)
MOJIBARE_CP1251 = ('ãî', 'ñî', 'ðî', 'äóõ', 'îáù', 'ñîöè', 'ôîðì', 'êóëüò', 'æèçí', 'ñòâî', 'ìåæäó', 'áûëî', '÷òîáû')
# UTF-8 read as Latin-1 (Ð³, Ð¾...)
MOJIBARE_UTF8 = ('Ð³', 'Ð¾', 'Ð´', 'Ð½', 'Ð¡', 'Ð ', 'ÐÐ')

def has_mojibake(text):
    return any(p in text for p in MOJIBARE_CP1251) or any(p in text for p in MOJIBARE_UTF8)

def try_cp1251_raw(raw):
    try:
        return raw.decode('cp1251')
    except UnicodeDecodeError:
        return raw.decode('cp1251', errors='replace')

def try_latin1_to_cp1251(text):
    """CP1251 bytes were read as Latin-1 and saved as UTF-8."""
    try:
        return text.encode('latin-1').decode('cp1251')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return None

def try_latin1_to_utf8(text):
    """UTF-8 bytes were read as Latin-1 and saved as UTF-8 (e.g. Ð³ = г)."""
    try:
        return text.encode('latin-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return None

# Type A: from fix_type_a.py
CHAR_MAP = {
    '\u040a': '\u041c', '\u040b': '\u041e', '\u0403': '\u0413', '\u0453': '\u0433',
    '\u040f': '\u041f', '\u040c': '\u041d', '\u201a': '\u0412', '\u0409': '\u041b',
    '\u2039': '\u041a', '\u0402': '\u0410', '\u201e': '\u0414', '\u2026': '\u0415',
    '\u20ac': '\u0418', '\ufffd': '\u0417', '\u201c': '\u0424', '\u040e': '\u0423',
    '\u2014': '\u0427', '\u2020': '\u0416', '\u2019': '\u0422', '\u2018': '\u0421',
    '\u2021': '\u0417', '\u0452': '\u0434', '\u045b': '\u0441', '\u045a': '\u043d',
    '\u045c': '\u044d',
}

def apply_type_a(text):
    for wrong, right in CHAR_MAP.items():
        text = text.replace(wrong, right)
    text = text.replace('. \u042c ', '. \u2116 ')
    text = text.replace(' \u0420 ', ' \u2014 ')
    return text

def apply_context_fixes(text):
    ctx = [
        ('доссия', 'Россия'), ('доссии', 'России'), ('доссийскаЯ', 'российская'),
        ('доссиЯне', 'россияне'), ('доссийский', 'российский'), ('даботающие', 'Работающие'),
        ('дазличиЯ', 'Различия'), ('Гогатые', 'Богатые'), ('дедактор', 'Редактор'),
        ('деклама', 'Реклама'), ('Кидерами', 'Лидерами'), ('Кюди', 'Люди'),
        ('Логда ', 'Когда '), ('Лак известно', 'Как известно'), ('Лакие ', 'Какие '),
        ('Л ним ', 'К ним '), ('Лак заметила', 'Как заметила'), ('Лроме того', 'Кроме того'),
        ('ГританскаЯ', 'Британская'), ('ќлизабет', 'Элизабет'), ('ќндрю', 'Эндрю'),
        ('ќклектика', 'Эклектика'), ('ќти характеристики', 'Эти характеристики'),
        ('Фход от', 'Исход от'), ('дечь идет', 'Речь идет'),
        # 001_Список, заголовок и специфичные замены
        ('ОгКАВКЕНИЕ', 'ОГЛАВЛЕНИЕ'), ('ОбКособенностЯх', 'Обособенностях'),
        ('Лолхас', 'Колхас'), ('Лирилл дожков', 'Кирилл Рожков'),
        ('дэм Колхас', 'Рем Колхас'), ('дсім Колхас', 'Рем Колхас'),
        # Зиммель: гЕОдг -> георг
        ('гЕОдг ', 'георг '), ('гЕОдг\n', 'георг\n'),
        # lotman_ocr
        ('Ю. М. Летная', 'Ю. М. Лотмана'), ('исторней', 'историей'),
        ('город как Симя', 'город как семья'), ('осповные', 'основные'), ('слелует', 'следует'),
        ('аслект', 'аспект'), ('Сидеологии', 'идеологии'), ('Пстра', 'Петра'),
    ]
    for old, new in ctx:
        text = text.replace(old, new)
    return text

def main():
    fixed_b = 0
    fixed_a = 0
    errs = []
    for rel in FILES:
        path = os.path.join(BASE, rel)
        if not os.path.isfile(path):
            errs.append((rel, 'not found'))
            continue
        with open(path, 'rb') as f:
            raw = f.read()

        text = None
        # Try UTF-8
        try:
            text = raw.decode('utf-8')
        except UnicodeDecodeError:
            text = None

        # If invalid UTF-8 or mojibake: try Type B fix
        if text is None:
            text = try_cp1251_raw(raw)
            if text is not None:
                fixed_b += 1
                print('Fixed (raw cp1251):', rel)
        elif has_mojibake(text):
            # UTF-8 mojibake (Ð³...) — try latin-1 → utf-8 first
            if any(p in text for p in MOJIBARE_UTF8):
                out = try_latin1_to_utf8(text)
                if out is not None:
                    text = out
                    fixed_b += 1
                    print('Fixed (latin-1→utf-8):', rel)
            # CP1251 mojibake (ãî...) — try latin-1 → cp1251
            if text and any(p in text for p in MOJIBARE_CP1251):
                out = try_latin1_to_cp1251(text)
                if out is not None:
                    text = out
                    fixed_b += 1
                    print('Fixed (latin-1→cp1251):', rel)

        if text is None:
            errs.append((rel, 'could not decode'))
            continue

        # Apply Type A
        before_a = text
        text = apply_type_a(text)
        text = apply_context_fixes(text)
        if text != before_a:
            fixed_a += 1
            print('Fixed (Type A):', rel)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)

    print('Done. Type B:', fixed_b, '| Type A:', fixed_a)
    for r, e in errs:
        print('  Error', r, e)
    return 0 if not errs else 1

if __name__ == '__main__':
    sys.exit(main())
