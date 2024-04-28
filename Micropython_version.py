"""
ESP32 Micropython version
"""

import urequests
import utime
from machine import Pin, Timer
from time import sleep
import time
import gc  # Import the garbage collector
import network
import json

# Initialize WiFi
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            time.sleep(1)
    print('Network config:', wlan.ifconfig())

connect_wifi('<SSID>', '<PASSWORD>')

# Telegram API settings
TOKEN = "<telegram token as a string>"
CHAT_ID = ["chat_id user 1", "chat_id user"]
ALLOWED_USERS_LIST = ["username1", "username2"]
URL = f"https://api.telegram.org/bot{TOKEN}/"

# Initialize variables
last_update_id = 0
door_sensor = Pin(12, Pin.IN, Pin.PULL_UP)
curr_state = "open" if door_sensor.value() else "locked"
print(curr_state)
led = Pin(22, Pin.OUT)
led_state = 1

RED_PIN = 3
GREEN_PIN = 4
BLUE_PIN = 5

#red_led = Pin(RED_PIN, Pin.OUT)
#green_led = Pin(GREEN_PIN, Pin.OUT)
#blue_led = Pin(BLUE_PIN, Pin.OUT)

ISRAEL_CLOCK_OFFSET = 3

last_message_time = 0  # <-- Added to track the last time a message was sent


#blue_led.value(1)


def fetch_current_time():
    try:
        response = urequests.get("http://worldtimeapi.org/api/timezone/Etc/UTC")
        data = response.json()
        datetime_str = data["datetime"]  # "2021-07-25T09:14:39.863748+00:00"

        # Extract individual components
        year = datetime_str[:4]
        month = datetime_str[5:7]
        day = datetime_str[8:10]
        hour = datetime_str[11:13]
        hour = str(int(hour) + ISRAEL_CLOCK_OFFSET)
        minute = datetime_str[14:16]

        # Reassemble in DD/MM/YY HH:MM format
        timestamp_str = f"{day}/{month}/{year[2:]} {hour}:{minute}"

        response.close()  # Close the response object to free resources
        gc.collect()  # Trigger garbage collection

        return timestamp_str
    except Exception as e:
        print("Error fetching time:", e)
        return None

def get_reply_markup():
    keyboard = {
        "keyboard": [[{"text": "check status"}]],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }
    return json.dumps(keyboard)

def send_telegram_message(message, chat_id_list=None):
    global last_message_time
    current_time = time.time()

    if not chat_id_list:
        chat_id_list = CHAT_ID  # If chat_id_list isn't provided, use CHAT_ID list

    if current_time - last_message_time >= 3:
        try:
            timestamp_str = fetch_current_time()
            if timestamp_str:
                full_message = f"[{timestamp_str}] {message}"
            else:
                full_message = message

            for participant in chat_id_list:
                try:
                    payload = {
                        'chat_id': participant,
                        'text': full_message,
                        'reply_markup': get_reply_markup()
                    }
                    response = urequests.post(URL + 'sendMessage', json=payload)
                    response.close()
                    print(f'sent a message "{full_message}" to chat ID {participant}')
                except Exception as ex:
                    print('Error in send_telegram_message:', ex)

            last_message_time = current_time
        except Exception as e:
            print('Error in send_telegram_message:', e)
            gc.collect()
    else:
        print('Skipped sending message to avoid flooding.')


def check_telegram_updates():
    global last_update_id
    try:
        gc.collect()
        response = urequests.get(URL + f"getUpdates?offset={last_update_id}")
        updates = response.json()
        gc.collect()
        for update in updates['result']:
            last_update_id = update['update_id'] + 1

            message = update.get('message')
            if not message:
                continue

            chat_id = message['chat'].get('id')
            if not chat_id:
                continue

            username = message['from'].get('username')
            if username not in ALLOWED_USERS_LIST:
                continue

            text = message.get('text')
            if text == '/status' or text == 'check status':
                send_telegram_message(f"The door is currently {curr_state}.", [chat_id])
    except Exception as e:
        print("Error while checking updates:", e)
        gc.collect()


# Timer and periodic function for checking Telegram
telegram_timer = Timer(-1)


def check_telegram_periodic(timer):
    check_telegram_updates()


telegram_timer.init(period=10000, mode=Timer.PERIODIC, callback=check_telegram_periodic)

#blue_led.value(0)

# Main loop
while True:
    new_state = "open" if door_sensor.value() else "locked"
    if new_state != curr_state:
        curr_state = new_state
        # send_telegram_message(f"Door is now {curr_state}.")
    gc.collect()
    # print(curr_state)
    if curr_state == "locked":
        led_state = 0
        #green_led.value(1)
        #red_led.value(0)
    elif curr_state == "open":
        led_state = not led_state
        #green_led.value(0)
        #red_led.value(1)
    led.value(led_state)

    time.sleep(0.1)  # Use time.sleep() for consistency
