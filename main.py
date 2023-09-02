import os

from dhooks import Embed, Webhook

webhook_url = os.environ["DISCORD_WEBHOOK_URL"]

def post_discord(embed: Embed):
    hook = Webhook(webhook_url)
    hook.send(embed=embed)


if __name__ == "__main__":
    embed = Embed()
    embed.set_title("hello", url="https://example.com")
    post_discord(embed)
