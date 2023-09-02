from enum import Enum
import os
import requests

from bs4 import BeautifulSoup
from dhooks import Embed, Webhook

TOP_URL = "https://www.ventforet.jp"
LOGO_URL = "https://cdn.www.ventforet.jp/system/images/club/95/original/27.png?1330092232"

class NEWS_TYPE(Enum):
    MATCH = 1 # 試合・イベント
    TEAM = 2 # チーム
    OTHER = 3 # その他

    @classmethod
    def get_names(cls) -> list:
        return [i.name for i in cls]


def webhook_url(news_type: NEWS_TYPE) -> str:
    if news_type == NEWS_TYPE.MATCH:
        return os.environ["DISCORD_WEBHOOK_URL_MATCH"]
    elif news_type == NEWS_TYPE.TEAM:
        return os.environ["DISCORD_WEBHOOK_URL_TEAM"]
    elif news_type == NEWS_TYPE.OTHER:
        return os.environ["DISCORD_WEBHOOK_URL_OTHER"]
    else:
        raise Exception("Unknown news type")

def get_url(news_type: NEWS_TYPE) -> str:
    if news_type == NEWS_TYPE.MATCH:
        return "https://www.ventforet.jp/news/match"
    elif news_type == NEWS_TYPE.TEAM:
        return "https://www.ventforet.jp/news/team"
    elif news_type == NEWS_TYPE.OTHER:
        return "https://www.ventforet.jp/news/other"
    else:
        raise Exception("Unknown news type")



def get_news_items(news_type: NEWS_TYPE) -> [dict]:
    url = get_url(news_type)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    news_item_elements = soup.find_all("a", class_="newsList__item")
    news_items = []
    for item in news_item_elements:
        href = item["href"]
        title = item.find(class_="top-news__information__detail").text
        release_id = href.split("/")[-1]
        # TODO: release_idの保存　・比較
        image = item.find(class_="newsList__itemImage").find("img")["src"]
        news_items.append({
            "full_url": "/".join([url, release_id]),
            "title": title,
            "image": image,
        })
    return news_items


def get_embed(title: str, url: str, image: str) -> Embed:
    embed = Embed()
    author_name = "ヴァンフォーレ甲府公式"
    embed.set_author(name=author_name, url=TOP_URL, icon_url=LOGO_URL)
    embed.set_title(title, url=url)
    embed.set_thumbnail(image)
    return embed


if __name__ == "__main__":
    for news_type_name in NEWS_TYPE.get_names():
        news_type = NEWS_TYPE[news_type_name]
        hook = Webhook(webhook_url(news_type))
        items = get_news_items(news_type)
        for item in items:
            embed = get_embed(item["title"], item["full_url"], item["image"])
            hook.send(embed=embed)
