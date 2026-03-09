# 13. Layout Constraints

Чтобы ничего не ломалось, агент должен соблюдать:

## Safe Area
– верхний отступ под topbar
– нижний отступ под nav / ticker
– внутренние padding внутри shell

## Width Rules
– контентные блоки должны иметь max-width
– длинный текст не должен растягиваться на всю ширину

## Height Rules
– если экран переполнен, дробить на два слайда
– не пытаться скрывать проблему через clipped overflow

## Grid Rules
– использовать responsive grid
– на узких экранах переводить 2–3 колонки в одну
– не держать 5–6 карточек в один ряд

## Typography Rules
– большие заголовки ограничивать clamp()
– body не опускать до нечитаемого размера

## Navigation Rules
– nav и progress всегда ниже safe content area
– ticker не перекрывает текст
– topbar не перекрывает hero headline
