import asyncio
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, BotCommand
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from config import TELEGRAM_BOT_TOKEN
from database import init_db, add_product, get_all_products, get_last_price, delete_product
from marketplace_scraper import scrape_product
from notifier import notify_user
from states import AddProductStates

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()

WATCHERS = {}

async def start_cmd(msg: Message):
    await msg.reply("Welcome to Product Tracker Bot! Use /add to add product link.")

async def add_product_cmd(msg: Message, state: FSMContext):
    await msg.reply("Please send me the product URL.")
    await state.set_state(AddProductStates.waiting_for_url)

async def process_product_url(msg: Message, state: FSMContext):
    url = msg.text
    product = scrape_product(url)

    if product is not None:
        add_product(url, product.price, product.available, msg.chat.id)
        await msg.reply(f"Added product {product.name}. Current price: ${product.price}, Available: {product.available}")
        await state.clear()
    else:
        await msg.reply("Failed to fetch product data. Please check the URL.")
        await state.clear()

async def cancel_cmd(msg: Message, state: FSMContext):
    await state.clear()
    await msg.reply("Operation cancelled.")

async def product_watcher():
    while True:
        for product in get_all_products():
            if len(product) < 4:
                continue

            product_url, price, available, chat_id = product
            product_data = scrape_product(product_url)

            if product_data is None:
                continue

            if product_data.price <= get_last_price(product_url):
                await notify_user(chat_id, f"Price dropped for {product_data.name}: ${product_data.price}")
            elif not get_last_price(product_url) and product_data.available:
                await notify_user(chat_id, f"{product_data.name} is back in stock!")

            add_product(product_url, product_data.price, product_data.available, chat_id)

        await asyncio.sleep(300)

async def list_products_cmd(msg: Message):
    products = get_all_products()
    if not products:
        await msg.reply("No products have been added yet.")
        return

    for product in products:
        if len(product) >= 3:
            product_info = f"URL: {product[0]}, Price: {product[1]}, Available: {product[2]}"
            await msg.reply(product_info)

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
router.message.register(cancel_cmd, Command(commands=["cancel"]))
router.message.register(process_product_url, StateFilter(AddProductStates.waiting_for_url))

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Start the bot"),
        BotCommand(command="/add", description="Add a product"),
        BotCommand(command="/list", description="List all products"),
        BotCommand(command="/delete", description="Delete a product"),
        BotCommand(command="/cancel", description="Cancel the current operation")
    ]
    await bot.set_my_commands(commands)

async def main():
    init_db()
    dp.include_router(router)
    await set_commands(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(product_watcher())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())