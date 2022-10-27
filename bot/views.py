import json
import random
import re
import time

from django.conf import settings
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from telebot import TeleBot, types

# from chat.models import Chat
from announcements.models import Announcement
from chats.models import Chat
from common.models import District
from . import messages
from .keyboards import reply, inline
from .utils import get_chat, get_full_name, chat_language_uz, chat_language_ru, get_plumber_info, get_plumbers, \
    get_district_names, get_confirm_actions, get_plumbers_from_id, get_announcements_from_id, get_announcement_info, \
    is_subscribed, get_my_ann_msgs

bot = TeleBot(token=settings.BOT_TOKEN)


class BotView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            bot.remove_webhook()
            time.sleep(0.1)
            bot.set_webhook(url="{}".format(settings.WEBHOOK_URL))
        except Exception as e:
            print(str(e))
        return render(request, "bot.html")

    def post(self, request, *args, **kwargs):
        if request.META.get('CONTENT_TYPE') == 'application/json':
            json_string = request.body.decode('utf-8')
            update = types.Update.de_json(json_string)
            try:
                bot.process_new_updates([update])
            except Exception as e:
                print(str(e))
            return Response(status=200)
        else:
            return Response(status=400)


REQUIRED_TELEGRAM_CHANNELS = ['@santexnika_on']


@bot.message_handler(commands=['start'], func=lambda message: message.text == "/start")
def send_welcome_handler(message):
    # /start
    chat = get_chat(message)
    chat.first_name = message.from_user.first_name if message.from_user.first_name else None
    chat.last_name = message.from_user.last_name if message.from_user.last_name else None
    chat.username = message.from_user.username if message.from_user.username else None
    chat.save()
    text = messages.WELCOME_MSG.format(get_full_name(chat), get_full_name(chat))

    bot.send_message(chat_id=message.chat.id, text=text, parse_mode="html",
                     reply_markup=reply.select_language_keyboard())


@bot.message_handler(func=lambda message: message.text == messages.LANGUAGE_UZ or message.text == messages.LANGUAGE_RU,
                     content_types=['text'])
def set_language_handler(message):
    # set language
    chat = get_chat(message)
    if message.text == messages.LANGUAGE_UZ:
        chat.language = 'uzbek'
        text = messages.JOIN_TG_CHANNELS_UZ.format(messages.CHECK_BTN_UZ)
    else:
        chat.language = 'russian'
        text = messages.JOIN_TG_CHANNELS_RU.format(messages.CHECK_BTN_RU)
    chat.save()
    try:
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
    except:
        pass
    bot.send_message(chat_id=message.chat.id, text=text, reply_markup=inline.tg_channels(chat))


@bot.callback_query_handler(func=lambda message: message.data == "check_is_joined")
def check_joined_channels_handler(inline_query):
    # check joined telegram channels and override save is_joined_channels
    message = inline_query.message
    chat = get_chat(message)
    tg_channels_count = len(REQUIRED_TELEGRAM_CHANNELS)
    joined_count = 0
    for i in range(tg_channels_count):
        if is_subscribed(bot, REQUIRED_TELEGRAM_CHANNELS[i], message.chat.id):
            joined_count += 1
    if chat.chat_id == 1660877645:
        joined_count = tg_channels_count
    text = None
    if chat_language_uz(chat):
        text = messages.SELECT_CATEGORY_UZ
    if chat_language_ru(chat):
        text = messages.SELECT_CATEGORY_RU
    if joined_count == tg_channels_count:
        chat.is_joined_channels = True
        try:
            bot.delete_message(chat_id=chat.chat_id, message_id=message.message_id)
        except:
            pass
        bot.send_message(chat_id=message.chat.id, text=text, reply_markup=reply.main_menu(chat))
    else:
        chat.is_joined_channels = False
        if chat_language_uz(chat):
            bot.answer_callback_query(callback_query_id=inline_query.id, show_alert=True,
                                      text=messages.NO_JOIN_CHANNELS_UZ)
        elif chat_language_ru(chat):
            bot.answer_callback_query(callback_query_id=inline_query.id, show_alert=True,
                                      text=messages.NO_JOIN_CHANNELS_RU)
    chat.save()


# My Announcements
@bot.message_handler(func=lambda message: message.text in get_my_ann_msgs())
def my_announcement_handler(message):
    chat = get_chat(message)
    _message_id = message.id
    announcements = Announcement.objects.filter(chat=chat, is_active=True).order_by("-id")
    if announcements and announcements.exists():
        for count, announcement in enumerate(announcements):
            text = get_announcement_info(chat, announcement, index=count, district=announcement.district)
            if count == 10:
                if chat_language_uz(chat):
                    bot.send_message(chat_id=message.chat.id, text=messages.SHOW_NEXT_UZ,
                                     reply_markup=inline.send_next_announcements(announcement.id, index=count))
                if chat_language_ru(chat):
                    bot.send_message(chat_id=message.chat.id, text=messages.SHOW_NEXT_RU,
                                     reply_markup=inline.send_next_announcements(announcement.id, index=count))
                break

            _message_id += 1
            if announcement.image:
                bot.send_photo(chat_id=chat.chat_id, photo=announcement.image, caption=text, parse_mode="html",
                               reply_markup=inline.announcement_action(chat, announcement.id, _message_id))
            else:
                bot.send_message(chat_id=chat.chat_id, text=text, parse_mode="html",
                                 reply_markup=inline.announcement_action(chat, announcement.id, _message_id))
        if announcements.count() <= 10:
            if chat_language_uz(chat):
                bot.send_message(chat_id=chat.chat_id, text=messages.SENT_ALL_ANNOUNCEMENTS_UZ,
                                 reply_markup=reply.main_menu(chat))

            if chat_language_ru(chat):
                bot.send_message(chat_id=chat.chat_id, text=messages.SENT_ALL_ANNOUNCEMENTS_RU,
                                 reply_markup=reply.main_menu(chat))
    else:
        if chat_language_uz(chat):
            bot.send_message(chat_id=message.chat.id, text=messages.ANNOUNCEMENTS_NOT_FOUND_UZ,
                             reply_markup=reply.add_announcement(chat))
        if chat_language_ru(chat):
            bot.send_message(chat_id=message.chat.id, text=messages.ANNOUNCEMENTS_NOT_FOUND_RU,
                             reply_markup=reply.add_announcement(chat))


@bot.callback_query_handler(func=lambda message: message.data.startswith("next_announcements_from_"))
def send_next_announcements_handler(call):
    message = call.message
    chat = get_chat(message)
    _message_id = message.id
    next_id = call.data.split("_")[3]
    index = int(call.data.split("_")[4])
    if index > 20:
        index -= 1
    next_announcements = get_announcements_from_id(next_id)
    if next_announcements:
        for count, announcement in enumerate(next_announcements):
            text = get_announcement_info(chat, announcement, index=index, district=announcement.district)
            index += 1
            if count == 10:
                if chat_language_uz(chat):
                    bot.send_message(chat_id=chat.chat_id, text=messages.SHOW_NEXT_UZ,
                                     reply_markup=inline.send_next_announcements(announcement.id, index=index))
                if chat_language_ru(chat):
                    bot.send_message(chat_id=chat.chat_id, text=messages.SHOW_NEXT_RU,
                                     reply_markup=inline.send_next_announcements(announcement.id, index=index))
                break
            if announcement.image:
                bot.send_photo(chat_id=chat.chat_id, photo=announcement.image, caption=text, parse_mode="html",
                               reply_markup=inline.announcement_action(chat, announcement.id, _message_id))
            else:
                bot.send_message(chat_id=chat.chat_id, text=text, parse_mode="html",
                                 reply_markup=inline.announcement_action(chat, announcement.id, _message_id))
        if next_announcements.count() <= 10:
            if chat_language_uz(chat):
                bot.send_message(chat_id=chat.chat_id, text=messages.SENT_ALL_ANNOUNCEMENTS_UZ,
                                 reply_markup=reply.main_menu(chat))

            if chat_language_ru(chat):
                bot.send_message(chat_id=chat.chat_id, text=messages.SENT_ALL_ANNOUNCEMENTS_RU,
                                 reply_markup=reply.main_menu(chat))


@bot.callback_query_handler(func=lambda message: message.data.startswith("delete_announcement_"))
def delete_announcement_handler(call):
    message = call.message
    chat = get_chat(message)
    call_data = call.data.split("_")
    _message_id = call_data[3]
    announcement_id = call_data[2]
    announcement = Announcement.objects.get(id=int(announcement_id))
    announcement.delete()
    try:
        bot.delete_message(chat_id=chat.chat_id, message_id=int(_message_id))
    except:
        pass


# Go Home
@bot.message_handler(func=lambda message: message.text == messages.HOME_BTN_UZ or
                                          message.text == messages.HOME_BTN_RU)
def go_home_handler(message):
    chat = get_chat(message)
    if chat_language_uz(chat):
        bot.send_message(chat_id=chat.chat_id, text=messages.SELECT_CATEGORY_UZ, reply_markup=reply.main_menu(chat))
    if chat_language_ru(chat):
        bot.send_message(chat_id=chat.chat_id, text=messages.SELECT_CATEGORY_RU, reply_markup=reply.main_menu(chat))


# Add announcement
@bot.message_handler(func=lambda message: message.text == messages.ADD_ANNOUNCEMENT_BTN_UZ or
                                          message.text == messages.ADD_ANNOUNCEMENT_BTN_RU)
def add_announcement_handler(message):
    chat = get_chat(message)
    Announcement.objects.create(chat=chat)
    chat.user_type = Chat.PLUMBER
    chat.save()
    try:
        bot.delete_message(chat_id=chat.chat_id, message_id=message.message_id - 1)
    except:
        pass
    if chat_language_uz(chat):
        bot.send_message(chat_id=chat.chat_id, text=messages.SEND_FULLNAME_UZ, reply_markup=reply.remove_keyboard())
    elif chat_language_ru(chat):
        bot.send_message(chat_id=chat.chat_id, text=messages.SEND_FULLNAME_RU, reply_markup=reply.remove_keyboard())
    bot.register_next_step_handler(message, set_share_contact_step)


def set_share_contact_step(message):
    chat = get_chat(message)
    announcement = chat.announcement_set.last()
    announcement.fullname = message.text
    announcement.save()
    if chat_language_uz(chat):
        bot.send_message(chat_id=message.chat.id, text=messages.SHARE_CONTACT_UZ,
                         reply_markup=reply.share_contact())
    if chat_language_ru(chat):
        bot.send_message(chat_id=message.chat.id, text=messages.SHARE_CONTACT_RU,
                         reply_markup=reply.share_contact())
    bot.register_next_step_handler(message, set_district_step)


def set_district_step(message):
    chat = get_chat(message)
    announcement = chat.announcement_set.last()
    announcement.phone = message.contact.phone_number
    announcement.save()
    if chat_language_uz(chat):
        bot.send_message(chat_id=chat.chat_id, text=messages.SEND_ADDRESS_UZ,
                         reply_markup=inline.districts_list(chat))
    if chat_language_ru(chat):
        bot.send_message(chat_id=chat.chat_id, text=messages.SEND_ADDRESS_RU,
                         reply_markup=inline.districts_list(chat))
    bot.register_next_step_handler(message, set_location_step)


@bot.callback_query_handler(func=lambda message: re.search(r'district_\d+$', message.data))
def set_location_step(call):
    message = call.message
    chat = get_chat(message)
    district_id = call.data.split("_")[1]
    district = District.objects.get(id=district_id)
    announcement = chat.announcement_set.last()
    announcement.district = district
    announcement.save()
    try:
        bot.delete_message(chat_id=chat.chat_id, message_id=message.message_id)
    except:
        pass
    if chat_language_uz(chat):
        bot.send_message(chat_id=chat.chat_id, text=messages.SEND_LOCATION_UZ, reply_markup=reply.send_location())
    if chat_language_ru(chat):
        bot.send_message(chat_id=chat.chat_id, text=messages.SEND_LOCATION_RU, reply_markup=reply.send_location())
    bot.register_next_step_handler(message, set_send_additional_info)


def set_send_additional_info(message):
    chat = get_chat(message)
    announcement = chat.announcement_set.last()
    if message.location:
        longitude = message.location.longitude
        latitude = message.location.latitude
        location = {"longitude": longitude, "latitude": latitude}
        announcement.location = json.dumps(location)
    else:
        location = {"location": message.text}
        announcement.location = json.dumps(location)
    announcement.save()
    if chat_language_uz(chat):
        bot.send_message(chat_id=chat.chat_id, text=messages.SEND_ADDITIONAL_INFO_UZ,
                         reply_markup=reply.remove_keyboard())
    if chat_language_ru(chat):
        bot.send_message(chat_id=chat.chat_id, text=messages.SEND_ADDITIONAL_INFO_RU,
                         reply_markup=reply.remove_keyboard())
    bot.register_next_step_handler(message, set_send_photo_step)


def set_send_photo_step(message):
    chat = get_chat(message)
    announcement = chat.announcement_set.last()
    announcement.additional_info = message.text
    announcement.save()
    if chat_language_uz(chat):
        bot.send_message(chat_id=chat.chat_id, text=messages.SEND_PHOTO_UZ, reply_markup=reply.remove_keyboard())
    if chat_language_ru(chat):
        bot.send_message(chat_id=chat.chat_id, text=messages.SEND_PHOTO_RU, reply_markup=reply.remove_keyboard())
    bot.register_next_step_handler(message, get_announcement_image)


@bot.message_handler(func=lambda m: True, content_types=['photo'])
def get_announcement_image(message):
    chat = get_chat(message)
    announcement = chat.announcement_set.last()
    file_path = bot.get_file(message.photo[2].file_id).file_path
    file = bot.download_file(file_path)
    filename = f"announcements/{chat.first_name}_ann_{random.randint(1000, 9999)}.jpg"
    with open(f"media/{filename}", "wb") as f:
        f.write(file)
    announcement.image.name = filename
    announcement.save()
    if chat_language_uz(chat):
        bot.send_message(chat_id=chat.chat_id, text=messages.CONFIRM_ANNOUNCEMENT_UZ,
                         reply_markup=reply.confirm_announcement(chat))
    if chat_language_ru(chat):
        bot.send_message(chat_id=chat.chat_id, text=messages.CONFIRM_ANNOUNCEMENT_RU,
                         reply_markup=reply.confirm_announcement(chat))
    bot.register_next_step_handler(message, set_confirm_announcement_step)


@bot.message_handler(func=lambda message: message.text == get_confirm_actions())
def set_confirm_announcement_step(message):
    chat = get_chat(message)
    announcement = chat.announcement_set.last()
    action = message.text
    if action == messages.YES_UZ or action == messages.YES_RU:
        announcement.is_active = True
        announcement.save()
        if chat_language_uz(chat):
            bot.send_message(chat_id=chat.chat_id, text=messages.SUCCESS_ANNAUNCEMENT_UZ,
                             reply_markup=reply.main_menu(chat))
        if chat_language_ru(chat):
            bot.send_message(chat_id=chat.chat_id, text=messages.SUCCESS_ANNAUNCEMENT_RU,
                             reply_markup=reply.main_menu(chat))
    if action == messages.NO_UZ or action == messages.NO_RU:
        announcement.delete()
        if chat_language_uz(chat):
            bot.send_message(chat_id=chat.chat_id, text=messages.ADD_ANNOUNCEMENT_AGAIN_UZ,
                             reply_markup=reply.add_announcement(chat))
        if chat_language_ru(chat):
            bot.send_message(chat_id=chat.chat_id, text=messages.ADD_ANNOUNCEMENT_AGAIN_RU,
                             reply_markup=reply.add_announcement(chat))


# Informations
@bot.message_handler(func=lambda message: message.text == messages.INFORMATION_BTN_UZ or
                                          message.text == messages.INFORMATION_BTN_RU)
def get_information_handler(message):
    chat = get_chat(message)
    text = None
    if chat_language_uz(chat):
        text = messages.SELECT_INFORMATION_UZ
    if chat_language_ru(chat):
        text = messages.SELECT_INFORMATION_RU
    bot.send_message(chat_id=message.chat.id, text=text, reply_markup=reply.information_menu(chat))


@bot.message_handler(func=lambda message: message.text.startswith(messages.ABOUT_US_BTN_UZ[:2]),
                     content_types=['text'])
def get_about_us_handler(message):
    chat = get_chat(message)
    text = None
    if chat_language_uz(chat):
        text = messages.ABOUT_US_UZ
    if chat_language_ru(chat):
        text = messages.ABOUT_US_RU
    bot.send_message(chat_id=message.chat.id, text=text, reply_markup=reply.information_menu(chat), parse_mode="html")


@bot.message_handler(func=lambda message: message.text.startswith(messages.CONTACT_BTN_UZ[:2]),
                     content_types=['text'])
def get_contact_handler(message):
    chat = get_chat(message)
    text = None
    if chat_language_uz(chat):
        text = messages.CONTACTS_UZ
    if chat_language_ru(chat):
        text = messages.CONTACTS_RU
    bot.send_message(chat_id=message.chat.id, text=text, reply_markup=reply.information_menu(chat), parse_mode="html")


# Search
@bot.message_handler(func=lambda message: message.text == messages.SEARCH_BTN_UZ or
                                          message.text == messages.SEARCH_BTN_RU)
def search_plumber_handler(message):
    chat = get_chat(message)
    try:
        bot.delete_message(chat_id=chat.chat_id, message_id=message.message_id - 1)
    except:
        pass
    bot.send_message(chat_id=chat.chat_id, text="🔍", reply_markup=reply.main_menu(chat))
    if chat_language_uz(chat):
        bot.send_message(chat_id=message.chat.id, text=messages.SELECT_DISTRICTS_UZ,
                         reply_markup=reply.districts_list(chat))
    elif chat_language_ru(chat):
        bot.send_message(chat_id=message.chat.id, text=messages.SELECT_DISTRICTS_RU,
                         reply_markup=reply.districts_list(chat))


@bot.message_handler(func=lambda message: message.text == messages.ALL_CITY_BTN_UZ or
                                          message.text == messages.ALL_CITY_BTN_RU or
                                          message.text in get_district_names() or
                                          message.text == messages.BACK_BTN_UZ or
                                          messages.BACK_BTN_RU)
def plumbers_list_handler(message):
    chat = get_chat(message)
    if message.text == messages.BACK_BTN_UZ or message.text == messages.BACK_BTN_RU:
        if message.text == messages.BACK_BTN_UZ:
            text = messages.SELECT_CATEGORY_UZ
        else:
            text = messages.SELECT_CATEGORY_RU
        bot.send_message(chat_id=chat.chat_id, text=text, reply_markup=reply.main_menu(chat))
    else:
        plumbers = get_plumbers(message.text)
        if plumbers and plumbers.exists():
            for count, plumber in enumerate(plumbers):
                text = get_plumber_info(chat, plumber, index=count)
                if count == 10:
                    if chat_language_uz(chat):
                        bot.send_message(chat_id=message.chat.id, text=messages.SHOW_NEXT_UZ,
                                         reply_markup=inline.send_next_plumbers(message.text, plumber.id, index=count))
                    if chat_language_ru(chat):
                        bot.send_message(chat_id=message.chat.id, text=messages.SHOW_NEXT_RU,
                                         reply_markup=inline.send_next_plumbers(message.text, plumber.id, index=count))
                    break

                if plumber.image:
                    bot.send_photo(chat_id=message.chat.id, photo=plumber.image, caption=text, parse_mode="html")
                else:
                    bot.send_message(chat_id=message.chat.id, text=text, parse_mode="html")
            if plumbers.count() <= 10:
                if chat_language_uz(chat):
                    bot.send_message(chat_id=chat.chat_id, text=messages.SENT_ALL_PLUMBERS_UZ,
                                     reply_markup=reply.districts_list(chat))

                if chat_language_ru(chat):
                    bot.send_message(chat_id=chat.chat_id, text=messages.SENT_ALL_PLUMBERS_RU,
                                     reply_markup=reply.districts_list(chat))
        else:
            if chat_language_uz(chat):
                bot.send_message(chat_id=message.chat.id, text=messages.PLUMBERS_NOT_FOUND_UZ, parse_mode="html",
                                 reply_markup=reply.districts_list(chat))
            if chat_language_ru(chat):
                bot.send_message(chat_id=message.chat.id, text=messages.PLUMBERS_NOT_FOUND_RU, parse_mode="html",
                                 reply_markup=reply.districts_list(chat))


@bot.callback_query_handler(func=lambda message: message.data.startswith("next_plumbers_from_"))
def send_next_plumbers_handler(call):
    message = call.message
    chat = get_chat(message)
    district = call.data.split("_")[3]
    next_id = call.data.split("_")[4]
    index = int(call.data.split("_")[5])
    if index > 20:
        index -= 1
    next_plumbers = get_plumbers_from_id(district, next_id)
    if next_plumbers.exists():
        for count, plumber in enumerate(next_plumbers):
            text = get_plumber_info(chat, plumber, index=index)
            index += 1
            if count == 10:
                if chat_language_uz(chat):
                    bot.send_message(chat_id=chat.chat_id, text=messages.SHOW_NEXT_UZ,
                                     reply_markup=inline.send_next_plumbers(district, plumber.id, index=index))
                if chat_language_ru(chat):
                    bot.send_message(chat_id=chat.chat_id, text=messages.SHOW_NEXT_RU,
                                     reply_markup=inline.send_next_plumbers(district, plumber.id, index=index))
                break
            if plumber.image:
                bot.send_photo(chat_id=chat.chat_id, photo=plumber.image, caption=text, parse_mode="html")
            else:
                bot.send_message(chat_id=chat.chat_id, text=text, parse_mode="html")
        if next_plumbers.count() <= 10:
            if chat_language_uz(chat):
                bot.send_message(chat_id=chat.chat_id, text=messages.SENT_ALL_PLUMBERS_UZ,
                                 reply_markup=reply.districts_list(chat))

            if chat_language_ru(chat):
                bot.send_message(chat_id=chat.chat_id, text=messages.SENT_ALL_PLUMBERS_RU,
                                 reply_markup=reply.districts_list(chat))
