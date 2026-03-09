# -*- coding: utf-8 -*-
"""Fix Type B mojibake: Kant/Cassirer file and seminar file. Run from repo root."""
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))

def fix_philosophy_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    # Replace curly quote (U+201C) used as wrong char
    text = text.replace('\u201cИКОСО\u201dИя философия', 'Философия')
    text = text.replace('\u201cилософиЯ', 'Философия')
    text = text.replace('\u201cрейд', 'Фрейд')
    text = text.replace('\u201cункциЯ', 'Функция')
    text = text.replace('\u201cундаментальнаЯ', 'Фундаментальная')
    # Я at end of word -> я (common pattern: letter+Я at end before space/punctuation)
    text = re.sub(r'([а-яё])Я\b', r'\1я', text)
    text = re.sub(r'сЯ\b', 'ся', text)
    text = re.sub(r'ниЯ\b', 'ния', text)
    text = re.sub(r'тиЯ\b', 'тия', text)
    text = re.sub(r'етсЯ\b', 'ется', text)
    text = re.sub(r'итсЯ\b', 'ится', text)
    text = re.sub(r'итсЯ\b', 'ится', text)
    text = re.sub(r'етсЯ\b', 'ется', text)
    text = re.sub(r'етсЯ\b', 'ется', text)
    # З...И as quotes -> «...»
    text = text.replace('ЗОпыт о человекеИ', '«Опыт о человеке»')
    text = text.replace('ЗДухИ', '«Дух»')
    text = text.replace('ЗсимволическойформеИ', '«символической форме»')
    text = text.replace('Змира впечатленийИ', '«мира впечатлений»')
    text = text.replace('Здуховных выраженийИ', '«духовных выражений»')
    text = text.replace('Зкак возможно познаниеИ', '«как возможно познание»')
    text = text.replace('ЗглавнаЯ', '«Главная')
    text = text.replace('ЗСимволическаЯ функциЯ или способностьИ', '«Символическая функция или способность»')
    text = text.replace('ЗоткрытиеИ', '«открытие»')
    text = text.replace('ЗрепрезентациЯИ', '«репрезентация»')
    text = text.replace('Зглубокое проникновение в формальную структуру реальностиИ', '«глубокое проникновение в формальную структуру реальности»')
    text = text.replace('ЗсамоосвобождениеИ', '«самоосвобождение»')
    text = text.replace('ЗидеальныйИ', '«идеальный»')
    text = text.replace('ЗсимволическойфункцииИ', '«символической функции»')
    text = text.replace('всеобщейЗсредойИ', 'всеобщей «средой»')
    text = text.replace(',Р путь', ', — путь')
    text = text.replace('ТидеальногоУ', '«идеального»')
    text = text.replace('образецИ', 'образец»')
    text = text.replace('культуреИ', 'культуре»')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print('Fixed:', path)

def fix_seminar_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    text = text.replace('ВизантиЯ', 'Византия')
    text = text.replace('Йристово', 'Христово')
    text = text.replace('Йристовых', 'Христовых')
    text = text.replace('Йристово', 'Христово')
    text = text.replace('Йристова', 'Христова')
    text = text.replace('Йристовой', 'Христовой')
    text = text.replace('Йристу', 'Христу')
    text = text.replace('Йриста', 'Христа')
    text = text.replace('Йристово', 'Христово')
    text = text.replace('Йристова', 'Христова')
    text = text.replace('Гог ', 'Бог ')
    text = text.replace('Гога ', 'Бога ')
    text = text.replace('Гожиих', 'Божиих')
    text = text.replace('ГожественныЯ', 'Божественная')
    text = text.replace('Гогоматери', 'Богоматери')
    text = text.replace('Гогоматере', 'Богоматери')
    text = text.replace('Фслышав', 'Услышав')
    text = text.replace('Фвидев', 'Увидев')
    text = text.replace('дождество', 'Рождество')
    text = text.replace('Лонец', 'Столпец')
    text = text.replace('Лоторый', 'Который')
    text = text.replace('осЯзали', 'осязали')
    text = text.replace('отличающеесЯ', 'отличающееся')
    text = text.replace('с Явленные', '— явленные')
    text = re.sub(r'([а-яё])Я\b', r'\1я', text)
    text = re.sub(r'сЯ\b', 'ся', text)
    text = re.sub(r'ниЯ\b', 'ния', text)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
    print('Fixed:', path)

if __name__ == '__main__':
    p1 = os.path.join(BASE, 'Мировая культура от палеолита до современности', 'Лекции_28_05', 'Философия символических форм', 'Философия симолических формc.txt')
    p2 = os.path.join(BASE, 'Мировая культура от палеолита до современности', 'Лекции_31_05', 'семинар_по_Древнерусскому_искусству', 'семинар_по_Древнерусскому_искусствус.txt')
    if os.path.isfile(p1):
        fix_philosophy_file(p1)
    if os.path.isfile(p2):
        fix_seminar_file(p2)
