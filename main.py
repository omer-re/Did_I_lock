#!/usr/bin/python3
# -*- coding: utf-8 -*-
from gpiozero import LED, Button
import timeit
import time
import emoji
from time import gmtime, strftime
from datetime import datetime
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler, CallbackQueryHandler
from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from secrets import TELEGRAM_BOT_TOKEN, ALLOWED_USERS_LIST

GreenLed = LED(22)
RedLed = LED(23)
button = Button(17)

global curr_state
curr_state = "unlocked"
prev_state = None
counter = 0
last_locked_time = None

# Check for new messages via API
production_bot = TELEGRAM_BOT_TOKEN
updater = Updater(production_bot, use_context=True)

# allows registering handler (command, text, video)
dispatcher = updater.dispatcher


# create a command callback function
def check_status(update, context):
    check_button = [[InlineKeyboardButton("Check", callback_data='Check')]]
    reply_markup1 = InlineKeyboardMarkup(check_button)
    if curr_state == "locked":
        string_to_translate1 = ":white_check_mark: Door was locked on {} and it is now {} :key:".format(
            last_locked_time, curr_state)
        translation1 = emoji.emojize(string_to_translate1, use_aliases=True, delimiters=(':', ':'))
        context.bot.send_message(chat_id=update.message.chat_id, text=translation1, reply_markup=reply_markup1)
    else:
        string_to_translate2 = " :x: Door is unlocked :unlocked: :bangbang:".format(last_locked_time, curr_state)
        translation2 = emoji.emojize(string_to_translate2, use_aliases=True, delimiters=(':', ':'))
        context.bot.send_message(chat_id=update.message.chat_id, text=translation2, reply_markup=reply_markup1)

# currently not working
def locked_for_minute():
    check_handler = CommandHandler("Check", check_status)
    dispatcher.add_handler(check_handler)


global button_handler
global check_handler
print("starting...")
while True:
    # restricting access to authorized users only.

    def C_B_button(bot, update):
        query = update.callback_query
        print(query)
        bot.edit_message_text(chat_id=query.message.chat.id, text=query.message.text,
                              message_id=query.message.message_id)


    button_handler = CallbackQueryHandler(C_B_button)
    dispatcher.add_handler(button_handler)
    check_handler = CommandHandler("Check", check_status)
    dispatcher.add_handler(CommandHandler("Check", check_status, Filters.user(username=ALLOWED_USERS_LIST)))

    dispatcher.add_handler(check_handler)

    # echo_handler = MessageHandler(Filters.text,check_status)
    # dispatcher.add_handler(echo_handler)
    time.sleep(1)
    if button.is_pressed:
        # print(curr_state)
        if prev_state == "unlocked":
            last_locked_time = strftime("%H:%M On %d.%m.%y", time.localtime())

        prev_state = curr_state
        curr_state = "locked"
        GreenLed.on()
        RedLed.off()
        counter = counter + 1

        if counter > 60:
            print(curr_state)
            # locked_for_minute()
            counter = 0

    else:
        prev_state = curr_state
        curr_state = "unlocked"
        # print(curr_state)
        GreenLed.off()
        RedLed.on()
        counter = 0

    updater.start_polling()

