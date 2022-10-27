from telebot import types

from bot import messages
from bot.utils import get_districts, chat_language_uz, chat_language_ru


def districts_list(chat):
    keyboard = types.InlineKeyboardMarkup()
    districts = get_districts(chat)
    first_col = districts[:len(districts) // 2]
    second_col = districts[len(districts) // 2:]
    for first_district, second_district in zip(first_col, second_col):
        keyboard.add(
            types.InlineKeyboardButton(text=first_district[1], callback_data=f"district_{first_district[0]}"),
            types.InlineKeyboardButton(text=second_district[1], callback_data=f"district_{second_district[0]}")
        )
    if len(first_col) != len(second_col):
        last_district = second_col[-1]
        keyboard.add(
            types.InlineKeyboardButton(text=last_district[1], callback_data=f"district_{last_district[0]}"),
        )

    return keyboard


def send_next_plumbers(district, next_id, index):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(text=messages.SHOW_NEXT_BTN,
                                   callback_data=f"next_plumbers_from_{district}_{next_id}_{index}"),
    )
    return keyboard


def send_next_announcements(next_id, index):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(text=messages.SHOW_NEXT_BTN,
                                   callback_data=f"next_announcements_from_{next_id}_{index}"),
    )
    return keyboard


def announcement_action(chat, announcement_id, message_id):
    keyboard = types.InlineKeyboardMarkup()
    if chat_language_uz(chat):
        keyboard.add(
            types.InlineKeyboardButton(
                text=messages.DELETE_MSG_UZ, callback_data=f"delete_announcement_{announcement_id}_{message_id}"
            ),
        )
    if chat_language_ru(chat):
        keyboard.add(
            types.InlineKeyboardButton(
                text=messages.DELETE_MSG_RU, callback_data=f"delete_announcement_{announcement_id}_{message_id}"
            ),
        )
    return keyboard


def tg_channels(chat):
    keyboard = types.InlineKeyboardMarkup()
    if chat_language_uz(chat):
        keyboard.add(types.InlineKeyboardButton(text="Santexnika", callback_data="tg_channel",
                                                url="https://t.me/santexnika_on"))
        keyboard.add(types.InlineKeyboardButton(text=messages.CHECK_BTN_UZ, callback_data="check_is_joined"))
    if chat_language_ru(chat):
        keyboard.add(types.InlineKeyboardButton(text="Santexnika", callback_data="tg_channel",
                                                url="https://t.me/santexnika_on"))
        keyboard.add(types.InlineKeyboardButton(text=messages.CHECK_BTN_RU, callback_data="check_is_joined"))
    return keyboard
