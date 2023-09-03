from enum import Enum
import os
import requests

from bs4 import BeautifulSoup
from cloudevents.http import CloudEvent
from dhooks import Embed, Webhook
from google.cloud import firestore


TOP_URL = "https://www.ventforet.jp"
LOGO_URL = "https://cdn.www.ventforet.jp/system/images/club/95/original/27.png?1330092232"


class NEWS_TYPE(Enum):
    MATCH = 1 # 試合・イベント
    TEAM = 2 # チーム
    OTHER = 3 # その他

    @classmethod
    def get_names(cls) -> list:
        return [i.name for i in cls]

# カテゴリごとにチャンネルを分けたいので、チャンネルごとにWebhookを作成している
def webhook_url(news_type: NEWS_TYPE) -> str:
    if news_type == NEWS_TYPE.MATCH:
        return os.environ["DISCORD_WEBHOOK_URL_MATCH"]
    elif news_type == NEWS_TYPE.TEAM:
        return os.environ["DISCORD_WEBHOOK_URL_TEAM"]
    elif news_type == NEWS_TYPE.OTHER:
        return os.environ["DISCORD_WEBHOOK_URL_OTHER"]
    else:
        raise Exception("Unknown news type")

# ニュースカテゴリ-ごとの一覧ぺージのURL
def index_url(news_type: NEWS_TYPE) -> str:
    if news_type == NEWS_TYPE.MATCH:
        return "https://www.ventforet.jp/news/match"
    elif news_type == NEWS_TYPE.TEAM:
        return "https://www.ventforet.jp/news/team"
    elif news_type == NEWS_TYPE.OTHER:
        return "https://www.ventforet.jp/news/other"
    else:
        raise Exception("Unknown news type")


# firestoreの初期化
db = firestore.Client()
latest_news_id_ref = db.collection("latest_news_id")

def get_latest_news_id(news_type: NEWS_TYPE) -> str:
    type_latest_id_ref = latest_news_id_ref.document(news_type.name)
    if type_latest_id_ref.get().exists:
        return type_latest_id_ref.get().to_dict()["id"]
    else:
        return ""

def update_latest_id(news_type: NEWS_TYPE, id: str) -> None:
    type_latest_id_ref = latest_news_id_ref.document(news_type.name)
    type_latest_id_ref.set({"id": id})


def get_news_items(news_type: NEWS_TYPE) -> [dict]:
    url = index_url(news_type)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    news_item_elements = soup.find_all("a", class_="newsList__item")
    saved_latest_id = get_latest_news_id(news_type)
    news_items = []
    for item in news_item_elements:
        href = item["href"]
        title = item.find(class_="top-news__information__detail").text

        news_id = href.split("/")[-1]
        if news_id == saved_latest_id:
            break

        image = item.find(class_="newsList__itemImage").find("img")["src"]
        news_items.append({
            "id": news_id,
            "full_url": "/".join([url, news_id]),
            "title": title,
            "image": image,
        })

    # 最新idを更新
    if len(news_items) > 0:
        latest_item = news_items[0]
        update_latest_id(news_type, latest_item["id"])

    # 古い順に送信されるようにする
    news_items.reverse()
    return news_items


def get_embed(news_title: str, news_url: str, news_image: str) -> Embed:
    embed = Embed()
    author_name = "ヴァンフォーレ甲府公式"
    embed.set_author(name=author_name, url=TOP_URL, icon_url=LOGO_URL)
    embed.set_title(news_title, url=news_url)
    embed.set_thumbnail(news_image)
    return embed


def main(event, context) -> None:
    print(event, context)
    for news_type_name in NEWS_TYPE.get_names():
        news_type = NEWS_TYPE[news_type_name]
        hook = Webhook(webhook_url(news_type))
        news_items = get_news_items(news_type)
        for item in news_items:
            embed = get_embed(item["title"], item["full_url"], item["image"])
            hook.send(embed=embed)
