import sqlite3

DB_NAME = "prices.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS product_prices (
                        url TEXT PRIMARY KEY,
                        last_price REAL
                     )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url TEXT UNIQUE,
                        chat_id INTEGER
                     )''')
    conn.commit()
    conn.close()

def get_last_price(url):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT last_price FROM product_prices WHERE url = ?", (url,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def update_price(url, price):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE product_prices SET last_price = ? WHERE url = ?", (price, url))
    conn.commit()
    conn.close()

def add_product(url, price=None, available=None, chat_id=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO products (url, chat_id) VALUES (?, ?)", (url, chat_id))
    if price is not None and available is not None:
        cursor.execute("INSERT INTO product_prices (url, last_price) VALUES (?, ?) ON CONFLICT(url) DO UPDATE SET last_price = ?",
                       (url, price, price))
    conn.commit()
    conn.close()

def delete_product(url):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM product_prices WHERE url = ?", (url,))
    cursor.execute("DELETE FROM products WHERE url = ?", (url,))
    conn.commit()
    conn.close()

def get_all_products():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT url, chat_id FROM products")
    rows = cursor.fetchall()
    conn.close()
    return rows


# Initialize database on first run
init_db()
