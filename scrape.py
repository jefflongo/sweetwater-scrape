import json
import requests
import schedule
import sys
import time

from config import *

HTTP_TIMEOUT_SECONDS: int = 30


class SweetwaterProduct:
    def __init__(self, name: str, serial: int, url: str, images: list) -> None:
        self.name: str = name
        self.serial: int = serial
        self.url: str = url
        self.images: list = images

    def __eq__(self, other) -> bool:
        if isinstance(other, SweetwaterProduct):
            return self.serial == other.serial
        return False

    def __hash__(self) -> int:
        return hash(self.serial)

    def __repr__(self) -> str:
        return repr(
            {
                "name": self.name,
                "serial": self.serial,
                "url": self.url,
                "images": self.images,
            }
        )


def post_discord(message: str, roles: list = []) -> None:
    if CONFIG_DISCORD_WEBHOOK != "":
        content: str = ""
        for role in roles:
            content += f"@{role} "
        content += f"\n\n{message}"
        data: dict = {"content": content, "username": "SweetwaterBot"}

        try:
            requests.post(
                CONFIG_DISCORD_WEBHOOK, json=data, timeout=HTTP_TIMEOUT_SECONDS
            )
        except requests.HTTPError as e:
            raise IOError(
                f"ERROR: failed to post to discord ({e.response.status_code})"
            ) from e


def get_products() -> set:
    headers: dict = {
        # otherwise we get a 403 error
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    }

    products: set = set()
    for product_id in CONFIG_PRODUCT_IDS:
        url: str = (
            f"https://www.sweetwater.com/webservices_sw/items/detail/{product_id}?format=serialcompare"
        )

        try:
            with requests.Session() as session:
                request = session.get(
                    url, headers=headers, timeout=HTTP_TIMEOUT_SECONDS
                )
        except requests.HTTPError as e:
            raise IOError(
                f"ERROR: failed to fetch products ({e.response.status_code})"
            ) from e
        try:
            data = json.loads(request.text)
        except json.JSONDecodeError as e:
            raise IOError("ERROR: Failed to parse product JSON") from e

        try:
            name: str = data["productName"]
            items: set = set(
                map(
                    lambda item: SweetwaterProduct(
                        name=name,
                        serial=int(item["serialNumber"]["number"]),
                        url=f'https://www.sweetwater.com{item["serialUrl"]}',
                        images=[
                            item["images"][view]["images"]["750"]["absolutePath"]
                            for view in [
                                "angle"
                            ]  # can optionally include body, front, back
                        ],
                    ),
                    data["comparableSerials"],
                )
            )
        except (KeyError, ValueError) as e:
            raise IOError("ERROR: Invalid key access when parsing product JSON") from e

        products |= items

    return products


def heartbeat() -> None:
    post_discord("SweetwaterBot is running.")


seen_products: set = get_products()


def scrape() -> None:
    global seen_products

    try:
        products: set = get_products()
        sold_products: set = seen_products - products
        new_products: set = products - seen_products

        for product in sold_products:
            message: str = (
                f"⚠️Listing Update⚠️\n{product.name} with serial number {product.serial} has been sold."
            )
            print(message)
            post_discord(message)

        for product in new_products:
            images: str = "\n".join(product.images)
            message: str = (
                f"❗New Listing Alert❗\n{product.name}\n{product.url}\n{images}\n"
            )
            print(message)
            post_discord(message, CONFIG_DISCORD_PING_ROLES)

        seen_products = products

    except IOError as e:
        print(e, file=sys.stderr)


if CONFIG_POST_HEARTBEAT:
    schedule.every().day.at("08:00").do(heartbeat)
schedule.every(CONFIG_REFRESH_RATE_SECONDS).seconds.do(scrape)

print(
    f"Starting Sweetwater scrape, with {len(seen_products)} "
    f"initial products from {len(CONFIG_PRODUCT_IDS)} product ID(s)\n"
)
for product in seen_products:
    images: str = "\n".join(product.images)
    message: str = f"{product.name}\n{product.url}\n{images}\n"
    print(message)


while True:
    t: int = schedule.idle_seconds()
    if t > 0:
        time.sleep(t)
    schedule.run_pending()
