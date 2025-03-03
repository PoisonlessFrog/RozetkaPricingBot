import requests
from bs4 import BeautifulSoup
from database import get_last_price, update_price
from product import Product

WEBHOOK_URL = "http://localhost:8000/webhook"  # Update with your actual server URL

def scrape_product(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    try:
        name = soup.find(class_="title__font").text.strip()
        price_text = soup.find(class_="product-price__big").text.strip()[:-1].replace("\u00A0", "")
        price = float(price_text)
        availability_label_class = soup.find(class_="status-label")['class']
        available = "status-label--green" in availability_label_class
        return Product(name, price, available)
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return None

def check_price_drop(url, chat_id):
    last_price = get_last_price(url) or float('inf')  # Default to a high value if no price exists
    product = scrape_product(url)
    if product and product.price < last_price:
        message = f"Price dropped! New price: ${product.price}"
        requests.post(WEBHOOK_URL, json={"message": message, "chat_id": chat_id})
        update_price(url, product.price)
    return product.price
