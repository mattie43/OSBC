import os
import requests
import json
from dotenv import load_dotenv


class Helpers:
    def __init__(self):
        load_dotenv()
        self.DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

    def _call_discord(self, content):
        WEBHOOK_URL = self.DISCORD_WEBHOOK
        headers = {
            "Content-Type": "application/json",
        }

        data = {"content": content}

        response = requests.post(WEBHOOK_URL, headers=headers, data=json.dumps(data))
        return response.status_code
