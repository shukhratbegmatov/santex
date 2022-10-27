from telebot import types

from bot import messages
from bot.utils import chat_language_uz, chat_language_ru, get_districts


def remove_keyboard():
    return types.ReplyKeyboardRemove()


def select_language_keyboard():
    md = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
    language_btn_uz = types.KeyboardButton(messages.LANGUAGE_UZ)
    language_btn_ru = types.KeyboardButton(messages.LANGUAGE_RU)
    md.row(language_btn_uz, language_btn_ru)
    return md


def share_contact():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(
        types.KeyboardButton(text="Share Contact", request_contact=True)
    )
    return keyboard


def send_location():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        types.KeyboardButton(text="Send Location", request_location=True)
    )
    return keyboard


def main_menu(chat):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if chat_language_uz(chat):
        keyboard.add(
            types.KeyboardButton(text=messages.SEARCH_BTN_UZ)
        )
        keyboard.add(
            types.KeyboardButton(text=messages.ADD_ANNOUNCEMENT_BTN_UZ)
        )
        keyboard.add(
            types.KeyboardButton(text=messages.INFORMATION_BTN_UZ),
            types.KeyboardButton(text=messages.MY_ANNOUNCEMENT_BTN_UZ),
        )
    if chat_language_ru(chat):
        keyboard.add(
            types.KeyboardButton(text=messages.SEARCH_BTN_RU)
        )
        keyboard.add(
            types.KeyboardButton(text=messages.ADD_ANNOUNCEMENT_BTN_RU)
        )
        keyboard.add(
            types.KeyboardButton(text=messages.INFORMATION_BTN_RU),
            types.KeyboardButton(text=messages.MY_ANNOUNCEMENT_BTN_RU),
        )
    return keyboard


def districts_list(chat):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    back_btn = None
    if chat_language_uz(chat):
        keyboard.add(
            types.KeyboardButton(text=messages.ALL_CITY_BTN_UZ)
        )
        back_btn = messages.BACK_BTN_UZ
    if chat_language_ru(chat):
        keyboard.add(
            types.KeyboardButton(text=messages.ALL_CITY_BTN_RU)
        )
        back_btn = messages.BACK_BTN_RU
    districts = get_districts(chat)
    first_col = districts[:len(districts) // 2]
    second_col = districts[len(districts) // 2:]
    for first_district, second_district in zip(first_col, second_col):
        keyboard.add(
            types.KeyboardButton(text=first_district[1]),
            types.KeyboardButton(text=second_district[1]),
        )
    if first_col != second_col:
        last_district = second_col[-1]
        keyboard.add(
            types.KeyboardButton(text=last_district[1]),
            types.KeyboardButton(text=back_btn),
        )
    else:
        keyboard.add(
            types.KeyboardButton(text=back_btn),
        )

    return keyboard


def announcement_districts_list(chat):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    districts = get_districts(chat)
    first_col = districts[:len(districts) // 2]
    second_col = districts[len(districts) // 2:]
    for first_district, second_district in zip(first_col, second_col):
        keyboard.add(
            types.KeyboardButton(text=first_district[1]),
            types.KeyboardButton(text=second_district[1]),
        )
    if first_col != second_col:
        last_district = second_col[-1]
        keyboard.add(
            types.KeyboardButton(text=last_district[1])
        )

    return keyboard


def information_menu(chat):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if chat_language_uz(chat):
        keyboard.add(
            types.KeyboardButton(text=messages.ABOUT_US_BTN_UZ),
            types.KeyboardButton(text=messages.CONTACT_BTN_UZ)
        )
        keyboard.add(
            types.KeyboardButton(text=messages.HOME_BTN_UZ),
        )
    if chat_language_ru(chat):
        keyboard.add(
            types.KeyboardButton(text=messages.ABOUT_US_BTN_RU),
            types.KeyboardButton(text=messages.CONTACT_BTN_RU)
        )
        keyboard.add(
            types.KeyboardButton(text=messages.HOME_BTN_RU),
        )
    return keyboard


def confirm_announcement(chat):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
    if chat_language_uz(chat):
        keyboard.add(
            types.KeyboardButton(text=messages.YES_UZ),
            types.KeyboardButton(text=messages.NO_UZ),
        )
    if chat_language_ru(chat):
        keyboard.add(
            types.KeyboardButton(text=messages.YES_RU),
            types.KeyboardButton(text=messages.NO_RU),
        )
    return keyboard


def add_announcement(chat):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if chat_language_uz(chat):
        keyboard.add(
            types.KeyboardButton(text=messages.ADD_ANNOUNCEMENT_BTN_UZ),
            types.KeyboardButton(text=messages.HOME_BTN_UZ),
        )
    if chat_language_ru(chat):
        keyboard.add(
            types.KeyboardButton(text=messages.ADD_ANNOUNCEMENT_BTN_RU),
            types.KeyboardButton(text=messages.HOME_BTN_RU),
        )
    return keyboard
