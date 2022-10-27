import json

from django.db.models import Q
from telebot.apihelper import ApiTelegramException

from announcements.models import Announcement
from bot import messages
from chats.models import Chat
from common.models import District


def get_chat(message):
    chat_instance, is_created = Chat.objects.get_or_create(chat_id=message.chat.id)
    return chat_instance


def get_full_name(chat):
    username = chat.username
    first_name = chat.first_name if chat.first_name else ''
    last_name = chat.last_name if chat.last_name else ''
    if first_name or last_name:
        return first_name + last_name
    return username


def chat_language_uz(chat):
    return chat.language == 'uzbek'


def chat_language_ru(chat):
    return chat.language == 'russian'


def get_districts(chat):
    if chat_language_uz(chat):
        return District.objects.values_list('id', 'name')
    elif chat_language_ru(chat):
        return District.objects.values_list('id', 'name_ru')


def get_district_names():
    districts = District.objects.values_list("name", "name_ru")
    districts_list = []
    for district in districts:
        districts_list.append(district[0])
        districts_list.append(district[1])
    return districts_list


def get_plumbers(msg):
    plumbers = None
    if msg == messages.ALL_CITY_BTN_UZ or msg == messages.ALL_CITY_BTN_RU:
        plumbers = Announcement.objects.filter(chat__user_type=Chat.PLUMBER, is_active=True).order_by("-id")
    if msg in get_district_names():
        plumbers = Announcement.objects.filter(
            Q(district__name=msg) | Q(district__name_ru=msg), chat__user_type=Chat.PLUMBER, is_active=True
        ).order_by("-id")
    return plumbers


def get_plumbers_from_id(msg, from_id):
    plumbers = None
    if msg == messages.ALL_CITY_BTN_UZ or msg == messages.ALL_CITY_BTN_RU:
        plumbers = Announcement.objects.order_by("-id").filter(
            id__lte=from_id, chat__user_type=Chat.PLUMBER, is_active=True
        )
    if msg in get_district_names():
        plumbers = Announcement.objects.order_by("-id").filter(
            Q(district__name=msg) | Q(district__name_ru=msg),
            id__lte=from_id, chat__user_type=Chat.PLUMBER, is_active=True
        )
    return plumbers


def get_announcements_from_id(from_id):
    return Announcement.objects.order_by("-id").filter(
        id__lte=from_id, chat__user_type=Chat.PLUMBER, is_active=True
    )


def get_plumber_info(chat, plumber, index):
    fullname = plumber.fullname if plumber.fullname else "-"
    phone = plumber.phone if plumber.phone else "-"
    username = plumber.chat.username if plumber.chat.username else "-"
    district, location = None, None
    if plumber.district:
        if chat_language_uz(chat):
            district = plumber.district.name
        if chat_language_ru(chat):
            district = plumber.district.name_ru
    else:
        district = "-"
    additional_info = plumber.additional_info if plumber.additional_info else "-"
    if "longitude" in plumber.location and "latitude" in plumber.location and plumber.location:
        lng = json.loads(plumber.location).get("longitude")
        ltd = json.loads(plumber.location).get("latitude")
        location = f'<a href="{make_location_link(lng, ltd)}">Location</a>'
    elif "location" in plumber.location and plumber.location:
        location = json.loads(plumber.location).get("location")
    _username = f"@{username}" if username != "-" else "-"
    text = None
    if chat_language_uz(chat):
        text = f"№{index + 1}\n<b>Ismi:</b> {fullname}\n" \
               f"<b>Ma'lumot:</b> {additional_info}\n" \
               f"<b>Tuman: </b> {district}\n" \
               f"<b>Manzil:</b> {location}\n" \
               f"<b>Telefon raqami:</b> {phone}\n" \
               f"<b>Username:</b> {_username}"
    if chat_language_ru(chat):
        text = f"№{index + 1}\n<b>Имя:</b> {fullname}\n" \
               f"<b>Информация:</b> {additional_info}\n" \
               f"<b>Район: </b> {district}\n" \
               f"<b>Адрес/b>: {location}\n" \
               f"<b>Номер телефона:</b> {phone}\n" \
               f"<b>Username:</b> {_username}"
    return text


def get_announcement_info(chat, plumber, index, district=None):
    fullname = plumber.fullname if plumber.fullname else "-"
    phone = plumber.phone if plumber.phone else "-"
    username = plumber.chat.username if plumber.chat.username else "-"
    if district:
        if chat_language_uz(chat):
            district = district.name
        if chat_language_ru(chat):
            district = district.name_ru
    else:
        district = "-"
    additional_info = plumber.additional_info if plumber.additional_info else "-"
    if "longitude" in plumber.location and "latitude" in plumber.location and plumber.location:
        lng = json.loads(plumber.location).get("longitude")
        ltd = json.loads(plumber.location).get("latitude")
        location = f'<a href="{make_location_link(lng, ltd)}">Location</a>'
    elif "location" in plumber.location and plumber.location:
        location = json.loads(plumber.location).get("location")
    else:
        location = "-"
    text = None
    _username = f"@{username}" if username != "-" else "-"
    if chat_language_uz(chat):
        text = f"№{index + 1}\n<b>Ismi:</b> {fullname}\n" \
               f"<b>Ma'lumot:</b> {additional_info}\n" \
               f"<b>Tuman: </b> {district}\n" \
               f"<b>Manzil:</b> {location}\n" \
               f"<b>Telefon raqami:</b> {phone}\n" \
               f"<b>Username:</b> {_username}"
    if chat_language_ru(chat):
        text = f"№{index + 1}\n<b>Имя:</b> {fullname}\n" \
               f"<b>Ma'lumot:</b> {additional_info}\n" \
               f"<b>Адрес/b>: {location}\n" \
               f"<b>Район: </b> {district}\n" \
               f"<b>Номер телефона:</b> {phone}\n" \
               f"<b>Username:</b> {_username}"
    return text


def get_confirm_actions():
    return [messages.YES_UZ, messages.YES_RU, messages.NO_UZ, messages.NO_RU]


def make_location_link(lng, lat):
    return f"https://maps.google.com/?q={lat},{lng}"


def is_subscribed(bot, chat_id, user_id):
    try:
        return True if bot.get_chat_member(chat_id, user_id).status == 'member' else False
    except ApiTelegramException as e:
        if e.result_json['description'] == 'Bad Request: user not found':
            return False


def get_my_ann_msgs():
    return [messages.MY_ANNOUNCEMENT_BTN_UZ, messages.MY_ANNOUNCEMENT_BTN_RU]
