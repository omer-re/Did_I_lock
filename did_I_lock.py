#!/usr/bin/python3
# -*- coding: utf-8 -*-
from gpiozero import LED, Button
import time
import emoji
from time import gmtime, strftime
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler, CallbackQueryHandler
from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from secrets import TELEGRAM_BOT_TOKEN, ALLOWED_USERS_LIST
import sheet

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

global wks
wks=sheet.open_sheet("https://docs.google.com/spreadsheets/d/1DLf9p4pRmMCpJnwdYXg8BVLiSfSp3eqiOaER4jeFOYs")

# create a command callback function
def check_status(update, context):
    check_button = [[InlineKeyboardButton("Check", callback_data='Check')]]
    reply_markup1 = InlineKeyboardMarkup(check_button)
    if curr_state == "locked":
        string_to_translate1 = ":white_check_mark: Door was last locked on {} and it is now {} :key:".format(
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

def blink_test(update=None, context=None):
    string_to_translate3 = "  :wink: Blink blink!  :wink:".format(last_locked_time, curr_state)
    translation3 = emoji.emojize(string_to_translate3, use_aliases=True, delimiters=(':', ':'))
    context.bot.send_message(chat_id=update.message.chat_id, text=translation3)
    for t in range(3):
        GreenLed.on()
        RedLed.off()
        time.sleep(0.1)
        GreenLed.off()
        RedLed.on()
        time.sleep(0.1)
        GreenLed.on()
        RedLed.off()
        time.sleep(0.1)
        GreenLed.off()
        RedLed.on()
        time.sleep(0.1)
        GreenLed.on()
        RedLed.off()
        time.sleep(0.2)
        GreenLed.off()
        RedLed.on()
        time.sleep(0.2)
        GreenLed.off()
        RedLed.off()
        time.sleep(0.2)
        GreenLed.on()
        RedLed.on()
        time.sleep(0.2)
        GreenLed.off()
        RedLed.off()
        time.sleep(0.2)
        GreenLed.on()
        RedLed.on()
        time.sleep(0.2)

    print("blink blink!")

def show_log(update=None, context=None):
    values_list=sheet.get_last_N_rows(wks,5)
    print(values_list)
    context.bot.send_message(chat_id=update.message.chat_id, text="**Last entries are:**")
    for row in range (0,5):
        if len(values_list[row])!=0:
            context.bot.send_message(chat_id=update.message.chat_id, text="\t\t{}\t\t{}\t\t{}".format(values_list[row][0],values_list[row][1],values_list[row][2]))




# prints the last 5 lines of the log
def log_data(state_to_log):
    last_locked_date = strftime("%d.%m.%y", time.localtime())
    last_locked_time = strftime("%H:%M", time.localtime())
    wks.append_row([str(last_locked_date),
                    str(last_locked_time),
                    str(state_to_log)])
    next_row = sheet.next_available_row(wks)


def C_B_button(bot, update):
        query = update.callback_query
        print(query)
        bot.edit_message_text(chat_id=query.message.chat.id, text=query.message.text,
                              message_id=query.message.message_id)


global button_handler
global check_handler
log_data("System start")
print("starting...")

button_handler = CallbackQueryHandler(C_B_button)
dispatcher.add_handler(button_handler)
check_handler = CommandHandler("Check", check_status)
dispatcher.add_handler(CommandHandler("Check", check_status, Filters.user(username=ALLOWED_USERS_LIST)))

blink_handler = CommandHandler("blink", blink_test)
dispatcher.add_handler(CommandHandler("blink", blink_test, Filters.user(username=ALLOWED_USERS_LIST)))
dispatcher.add_handler(blink_handler)

showlog_handler = CommandHandler("log", show_log)
dispatcher.add_handler(CommandHandler("log", show_log, Filters.user(username=ALLOWED_USERS_LIST)))
dispatcher.add_handler(showlog_handler)
#blink_test()
while True:
    # restricting access to authorized users only.



    # echo_handler = MessageHandler(Filters.text,check_status)
    # dispatcher.add_handler(echo_handler)

    # artificial delay to reduce noises
    time.sleep(1)

    if button.is_pressed:
        # print(curr_state)
        GreenLed.on()
        RedLed.off()
        # means change of state
        #if prev_state == "unlocked":
        if counter == 0:
            last_locked_time = strftime("%H:%M \t %d.%m.%y", time.localtime())
            log_data("locked")

        prev_state = curr_state
        curr_state = "locked"

        counter = counter + 1

        # counter as a helper for control
        if counter % 60==0:
            print(curr_state)
            RedLed.on()
            #counter = 0

    else:
        # means change of state
        #if prev_state == "locked":
        if counter !=0:
            log_data("unlocked")

        prev_state = curr_state
        curr_state = "unlocked"
        # print(curr_state)
        GreenLed.off()
        RedLed.on()
        counter = 0

    updater.start_polling()

