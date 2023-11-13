import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")


def call_discord(content):
    headers = {
        "Content-Type": "application/json",
    }

    data = {"content": content}

    response = requests.post(DISCORD_WEBHOOK, headers=headers, data=json.dumps(data))
    return response.status_code
