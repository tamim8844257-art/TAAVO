from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os

app = FastAPI(title="TAAVO", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "taavo.db")


def db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def setup_database():
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL,
            currency TEXT NOT NULL,
            moq INTEGER NOT NULL,
            country TEXT NOT NULL,
            seller TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS buyer_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT NOT NULL,
            quantity TEXT NOT NULL,
            destination TEXT NOT NULL,
            details TEXT,
            buyer TEXT
        )
    """)

    conn.commit()
    conn.close()


setup_database()


@app.get("/")
def home():
    return {
        "success": True,
        "message": "TAAVO Backend is running!",
        "platform": "TAAVO - Trade Without Borders"
    }


@app.get("/api/status")
def status():
    return {
        "success": True,
        "message": "TAAVO API is working",
        "backend": "online",
        "database": "connected"
    }


@app.post("/api/signup")
def signup(data: dict):
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")
    role = data.get("role", "buyer")

    if not name or not email or not password:
        return {
            "status": "error",
            "message": "Name, email and password are required"
        }

    conn = db()
    cur = conn.cursor()

    cur.execute(
        "SELECT id FROM users WHERE LOWER(email)=LOWER(?)",
        (email,)
    )

    if cur.fetchone():
        conn.close()
        return {
            "status": "error",
            "message": "Email already registered"
        }

    cur.execute(
        """
        INSERT INTO users (name, email, password, role)
        VALUES (?, ?, ?, ?)
        """,
        (name, email, password, role)
    )

    user_id = cur.lastrowid

    conn.commit()
    conn.close()

    return {
        "status": "success",
        "message": "TAAVO account created successfully",
        "user": {
            "id": user_id,
            "name": name,
            "email": email,
            "role": role
        }
    }


@app.post("/api/login")
def login(data: dict):
    email = data.get("email", "").strip()
    password = data.get("password", "")

    conn = db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, name, email, role
        FROM users
        WHERE LOWER(email)=LOWER(?)
        AND password=?
        """,
        (email, password)
    )

    user = cur.fetchone()
    conn.close()

    if not user:
        return {
            "status": "error",
            "message": "Invalid email or password"
        }

    return {
        "status": "success",
        "message": "Login successful",
        "user": dict(user)
    }


@app.post("/api/products")
def create_product(data: dict):
    try:
        name = data.get("name", "").strip()
        description = data.get("description", "").strip()
        price = float(data.get("price", 0))
        currency = data.get("currency", "USD")
        moq = int(data.get("moq", 1))
        country = data.get("country", "").strip()
        seller = data.get("seller", "Unknown Seller")

        if not name or not description or not country:
            return {
                "status": "error",
                "message": "Product name, description and country are required"
            }

        conn = db()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO products
            (name, description, price, currency, moq, country, seller)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                description,
                price,
                currency,
                moq,
                country,
                seller
            )
        )

        product_id = cur.lastrowid

        conn.commit()
        conn.close()

        product = {
            "id": product_id,
            "name": name,
            "description": description,
            "price": price,
            "currency": currency,
            "moq": moq,
            "country": country,
            "seller": seller
        }

        return {
            "status": "success",
            "message": "Product published successfully",
            "product_id": product_id,
            "product": product
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@app.get("/api/products")
def get_products():
    conn = db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM products ORDER BY id DESC")
    products = [dict(row) for row in cur.fetchall()]

    conn.close()

    return {
        "status": "success",
        "products": products
    }


@app.post("/api/buyer-requests")
def create_buyer_request(data: dict):
    product = data.get("product", "").strip()
    quantity = str(data.get("quantity", "")).strip()
    destination = data.get("destination", "").strip()
    details = data.get("details", "")
    buyer = data.get("buyer", "Unknown Buyer")

    if not product or not quantity or not destination:
        return {
            "status": "error",
            "message": "Product, quantity and destination are required"
        }

    conn = db()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO buyer_requests
        (product, quantity, destination, details, buyer)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            product,
            quantity,
            destination,
            details,
            buyer
        )
    )

    request_id = cur.lastrowid

    conn.commit()
    conn.close()

    return {
        "status": "success",
        "message": "Buyer request submitted successfully",
        "request_id": request_id
    }


@app.get("/api/buyer-requests")
def get_buyer_requests():
    conn = db()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM buyer_requests ORDER BY id DESC"
    )

    requests = [dict(row) for row in cur.fetchall()]

    conn.close()

    return {
        "status": "success",
        "requests": requests
    }