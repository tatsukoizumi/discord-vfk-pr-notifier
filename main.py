import os

from dhooks import Embed, Webhook

import requests
from bs4 import BeautifulSoup

webhook_url = os.environ["DISCORD_WEBHOOK_URL"]

def post_discord(embed: Embed):
    hook = Webhook(webhook_url)
    hook.send(embed=embed)

def get_html() -> [dict]:
    url = "https://www.ventforet.jp/news/match"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    news_item_elements = soup.find_all("a", class_="newsList__item")
    items = []
    for item in news_item_elements:
        href = item["href"]
        title = item.find(class_="top-news__information__detail").text
        release_id = href.split("/")[-1]
        path = href.rsplit("/", 1)[0]
        image = item.find(class_="newsList__itemImage").find("img")["src"]
        items.append({
            "full_url": "/".join([url, release_id]),
            "title": title,
            "id": release_id,
            "image": image,
            "path": path
        })
    return items

if __name__ == "__main__":
    items = get_html()
    for item in items[0:1]:
        embed = Embed()
        embed.set_title(item['title'], url=item["full_url"])
        embed.set_image(item["image"])
        post_discord(embed)
