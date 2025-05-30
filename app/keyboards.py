from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def confirm_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="✅ Oui", callback_data="yes"),
            InlineKeyboardButton(text="❌ Non", callback_data="no"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
