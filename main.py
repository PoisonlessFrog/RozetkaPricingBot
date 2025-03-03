import asyncio

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message

from config import TELEGRAM_BOT_TOKEN
from database import init_db, add_product, get_all_products, get_last_price, delete_product
from marketplace_scraper import scrape_product
from notifier import notify_user

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
router = Router()

WATCHERS = {}

async def start_cmd(msg: Message):
    await msg.reply("Welcome to Product Tracker Bot! Use /add to add product link.")

async def add_product_cmd(msg: Message):
    args = msg.text.split(maxsplit=1)
    if len(args) < 2:
        await msg.reply("Usage: /add <product-url>")
        return

    url = args[1]
    product = scrape_product(url)

    if product is not None:
        add_product(url, product.price, product.available, msg.chat.id)
        await msg.reply(f"Added product {product.name}. Current price: ${product.price}, Available: {product.available}")
    else:
        await msg.reply("Failed to fetch product data. Please check the URL.")

async def product_watcher():
    while True:
        for product_url, chat_id in get_all_products():
            product = scrape_product(product_url)

            if product is None:
                continue

            if product.price <= get_last_price(product_url):
                await notify_user(chat_id, f"Price dropped for {product.name}: ${product.price}")
            elif not get_last_price(product_url) and product.available:
                await notify_user(chat_id, f"{product.name} is back in stock!")

            add_product(product_url, product.price, product.available, chat_id)

        await asyncio.sleep(300)


async def list_products_cmd(msg: Message):
    products = get_all_products()
    if not products:
        await msg.reply("No products have been added yet.")
        return

    product_list = "\n".join(products)
    await msg.reply(f"List of added products:\n{product_list}")

async def delete_product_cmd(msg: Message):
    args = msg.text.split(maxsplit=1)
    if len(args) < 2:
        await msg.reply("Usage: /delete <product-url>")
        return

    url = args[1]
    delete_product(url)
    WATCHERS.pop(url, None)
    await msg.reply(f"Deleted product with URL: {url}")

router.message.register(delete_product_cmd, Command(commands=["delete"]))
router.message.register(start_cmd, Command(commands=["start"]))
router.message.register(add_product_cmd, Command(commands=["add"]))
router.message.register(list_products_cmd, Command(commands=["list"]))


async def main():
    init_db()
    dp.include_router(router)
    loop = asyncio.get_event_loop()
    loop.create_task(product_watcher())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())