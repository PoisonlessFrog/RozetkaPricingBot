# Product Tracker Telegram Bot

This is a Telegram bot to track product prices and availability from online stores.

## Features
- Add product links from supported marketplaces
- Track price changes
- Notify on price drop or restock

## Commands
- `/start` - Welcome message
- `/add <product-url>` - Add product to watchlist

## Running via Docker
1. Place your bot token into `docker-compose.yml`.
2. Run: `docker compose up -d`
3. Products and data persist in the `./data` folder.

## Requirements
- Python 3.12+
- Docker (for deployment)
