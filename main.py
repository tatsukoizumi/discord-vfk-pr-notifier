from enum import Enum
import os
import requests

from bs4 import BeautifulSoup
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


db = firestore.Client()

ref = db.collection("latest_news_id")

def get_news_items(news_type: NEWS_TYPE) -> [dict]:
    url = index_url(news_type)
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    news_item_elements = soup.find_all("a", class_="newsList__item")
    news_items = []
    print('hi')
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


if __name__ == "__main__":
    for doc in ref.stream():
        print('yes')
        print(f'{doc.id} => {doc.to_dict()}')
    for news_type_name in NEWS_TYPE.get_names():
        news_type = NEWS_TYPE[news_type_name]
        hook = Webhook(webhook_url(news_type))
        news_items = get_news_items(news_type)
        for item in news_items:
            embed = get_embed(item["title"], item["full_url"], item["image"])
            # hook.send(embed=embed)
