import json
from urllib.request import Request, urlopen
import os

webhook_url = os.environ["DISCORD_WEBHOOK_URL"]

def post_discord(message: str, webhook_url: str):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "DiscordBot (private use) Python-urllib/3.10",
    }
    data = {"content": message}
    request = Request(
        webhook_url,
        data=json.dumps(data).encode(),
        headers=headers,
    )

    with urlopen(request) as res:
        assert res.getcode() == 204


if __name__ == "__main__":
    post_discord("hello", webhook_url)
