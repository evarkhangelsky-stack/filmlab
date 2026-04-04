import sqlite3
import json
from typing import List, Dict, Any

DB_NAME = "shop.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            user_id INTEGER,
            product_id TEXT,
            quantity INTEGER,
            PRIMARY KEY (user_id, product_id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            items TEXT,
            subtotal INTEGER,
            total INTEGER,
            payment_method TEXT,
            status TEXT,
            pickup_station TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            tracking_number TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_to_cart(user_id: int, product_id: str, quantity: int = 1):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?) "
                "ON CONFLICT(user_id, product_id) DO UPDATE SET quantity = quantity + ?",
                (user_id, product_id, quantity, quantity))
    conn.commit()
    conn.close()

def remove_from_cart(user_id: int, product_id: str):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM cart WHERE user_id = ? AND product_id = ?", (user_id, product_id))
    conn.commit()
    conn.close()

def set_quantity(user_id: int, product_id: str, quantity: int):
    if quantity <= 0:
        remove_from_cart(user_id, product_id)
    else:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?) "
                    "ON CONFLICT(user_id, product_id) DO UPDATE SET quantity = ?",
                    (user_id, product_id, quantity, quantity))
        conn.commit()
        conn.close()

def get_cart(user_id: int) -> Dict[str, int]:
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT product_id, quantity FROM cart WHERE user_id = ?", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return {pid: qty for pid, qty in rows}

def clear_cart(user_id: int):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DELETE FROM cart WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def create_order(user_id: int, items: List[Dict], subtotal: int, total: int,
                 payment_method: str, pickup_station: str) -> int:
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO orders (user_id, items, subtotal, total, payment_method, status, pickup_station)
        VALUES (?, ?, ?, ?, ?, 'pending', ?)
    """, (user_id, json.dumps(items), subtotal, total, payment_method, pickup_station))
    order_id = cur.lastrowid
    conn.commit()
    conn.close()
    clear_cart(user_id)
    return order_id

def get_user_orders(user_id: int) -> List[Dict]:
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    rows = cur.fetchall()
    orders = []
    for row in rows:
        orders.append({
            "order_id": row["order_id"],
            "items": json.loads(row["items"]),
            "subtotal": row["subtotal"],
            "total": row["total"],
            "payment_method": row["payment_method"],
            "status": row["status"],
            "pickup_station": row["pickup_station"],
            "created_at": row["created_at"],
            "tracking_number": row["tracking_number"]
        })
    conn.close()
    return orders

def update_order_status(order_id: int, status: str, tracking_number: str = None):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    if tracking_number:
        cur.execute("UPDATE orders SET status = ?, tracking_number = ? WHERE order_id = ?",
                    (status, tracking_number, order_id))
    else:
        cur.execute("UPDATE orders SET status = ? WHERE order_id = ?", (status, order_id))
    conn.commit()
    conn.close()
