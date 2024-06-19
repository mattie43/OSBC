import os
import requests
import json
import time
from dotenv import load_dotenv
import utilities.imagesearch as imsearch
import pyautogui as pag

load_dotenv()
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")
PASSWORD = os.getenv("PASSWORD")


def call_discord(content):
    headers = {
        "Content-Type": "application/json",
    }

    data = {"content": content}

    response = requests.post(DISCORD_WEBHOOK, headers=headers, data=json.dumps(data))
    return response.status_code


def login(screenshot):
    # use screenshot to find login btn
    # login with pass only, (username should be remembered)
    # return True when done, False if can't find login splash
    return ""
