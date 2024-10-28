from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types

keyboard_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Сообщить ⚠", callback_data='problem'), types.InlineKeyboardButton(text="Посмотреть 📋", callback_data='show')],[types.InlineKeyboardButton(text="Мои проблемы 👀", callback_data='my')]
    ])

keyboard_add_prob = InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="✅ Продолжить добавление", callback_data='contin_add')],[types.InlineKeyboardButton(text="Отменить отправку ❌", callback_data='wrong_add')]
    ])

keyboard_adding = InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Опубликовать проблему⤴", callback_data='adding')],[types.InlineKeyboardButton(text="Отменить отправку ❌", callback_data='wrong_add')]
    ])

keyboard_myproblem = InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Обновить список проблем 🔄", callback_data='update')],[types.InlineKeyboardButton(text="Взять проблему 📎", callback_data='take_problem')],[types.InlineKeyboardButton(text="Скрыть список 👀", callback_data='wrong_add')]
    ])

keyboard_wrong_add = InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Отменить отправку ❌", callback_data='wrong_add')]
    ])

keyboard_vid = InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="ℹ ИНФОРМАЦИОННЫЙ", callback_data='vid INFO')],[types.InlineKeyboardButton(text="❗ПРЕДУПРЕЖДАЮЩИЙ", callback_data='vid WARN')],[types.InlineKeyboardButton(text="⚠ КРИТИЧЕСКИЙ", callback_data='vid CRIT')]
    ])

keyboard_my = InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Завершить проблему🏁", callback_data='finish')],[types.InlineKeyboardButton(text="Скрыть список 👀", callback_data='wrong_add')]
    ])

keyboard_type = InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Общее", callback_data='type 1'), types.InlineKeyboardButton(text="Электрика", callback_data='type 3')],
        [types.InlineKeyboardButton(text="Безопасность", callback_data='type 4'), types.InlineKeyboardButton(text="Закупки", callback_data='type 7')],
        [types.InlineKeyboardButton(text="Руководство", callback_data='type 5'), types.InlineKeyboardButton(text="Логистика", callback_data='type 9')],
        [types.InlineKeyboardButton(text="Охрана труда", callback_data='type 6'), types.InlineKeyboardButton(text="Сети, связи", callback_data='type 10')],
        [types.InlineKeyboardButton(text="Программирование", callback_data='type 8'), types.InlineKeyboardButton(text="Химия", callback_data='type 2')]
    ])
