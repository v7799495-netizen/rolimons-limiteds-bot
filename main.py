
import os
import time
import json
import logging
import requests
from bs4 import BeautifulSoup

TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
URL = "https://www.rolimons.com/free-roblox-limiteds"
SEEN_FILE = "seen.json"

logging.basicConfig(level=logging.INFO)
session = requests.Session()
session.headers["User-Agent"] = "Mozilla/5.0"

def send(text):
    r = session.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": text},
        timeout=20,
    )
    r.raise_for_status()

def get_items():
    r = session.get(URL, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    items = {}

    for link in soup.select('a[href*="/item/"]'):
        card = link
        for _ in range(4):
            if card.parent:
                card = card.parent

        text = card.get_text(" ", strip=True)
        import re
        m = re.search(r"(?:stock|copies|available)\s*[:\-]?\s*([\d,]+)", text, re.I)
        if not m:
            continue

        stock = int(m.group(1).replace(",", ""))
        if stock < 50:
            continue

        href = link.get("href", "")
        if href.startswith("/"):
            href = "https://www.rolimons.com" + href

        title = link.get_text(" ", strip=True) or "Roblox Limited"
        items[href] = (title, stock)

    return items

def main():
    try:
        with open(SEEN_FILE, encoding="utf-8") as f:
            seen = set(json.load(f))
    except (OSError, ValueError):
        seen = set()

    send("🤖 Бот запущен! Ищу лимитки со стоком от 50 копий.")
    while True:
        try:
            for url, (title, stock) in get_items().items():
                if url in seen:
                    continue
                send(f"🆕 {title}\n📦 Сток: {stock}\n🔗 {url}")
                seen.add(url)
                with open(SEEN_FILE, "w", encoding="utf-8") as f:
                    json.dump(sorted(seen), f)
        except Exception:
            logging.exception("Ошибка проверки Rolimons")
        time.sleep(300)

if __name__ == "__main__":
    main()
