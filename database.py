import sqlite3

DB_NAME = "prices.db"

def init_db():
    conn = sqlite3.connect('prices.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            url TEXT PRIMARY KEY,
            price REAL,
            available INTEGER,
            chat_id INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def get_last_price(url):
    conn = sqlite3.connect('prices.db')
    cursor = conn.cursor()
    cursor.execute('SELECT price FROM products WHERE url = ?', (url,))
    price = cursor.fetchone()
    conn.close()
    return price[0] if price else None

def update_price(url, price):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE product_prices SET last_price = ? WHERE url = ?", (price, url))
    conn.commit()
    conn.close()

def add_product(url, price, available, chat_id):
    conn = sqlite3.connect('prices.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO products (url, price, available, chat_id)
        VALUES (?, ?, ?, ?)
    ''', (url, price, available, chat_id))
    conn.commit()
    conn.close()

def delete_product(url):
    conn = sqlite3.connect('prices.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE url = ?', (url,))
    conn.commit()
    conn.close()

def get_all_products():
    conn = sqlite3.connect('prices.db')
    cursor = conn.cursor()
    cursor.execute('SELECT url, price, available FROM products')
    products = cursor.fetchall()
    conn.close()
    return products


# Initialize database on first run
init_db()
