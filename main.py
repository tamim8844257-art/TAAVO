from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import os

app = FastAPI(
    title="TAAVO",
    version="3.0.0",
    description="TAAVO — Trade Without Borders"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# IN-MEMORY MVP DATA
# =========================================================

users = {}
products = []
buyer_requests = []
orders = []
payments = []


# =========================================================
# MODELS
# =========================================================

class SignupData(BaseModel):
    name: str
    email: str
    password: str
    role: str = "Buyer"


class LoginData(BaseModel):
    email: str
    password: str


class BuyerRequestData(BaseModel):
    requirement: str
    quantity: Optional[str] = ""
    budget: Optional[str] = ""
    currency: Optional[str] = "USD"
    targetCountry: Optional[str] = ""


class ProductData(BaseModel):
    name: str
    description: Optional[str] = ""
    price: float
    currency: str = "USD"
    moq: float = 1
    country: str
    seller: str = "Unknown Seller"


class SellerReplyData(BaseModel):
    requestId: int
    seller: str = "TAAVO Seller"
    message: str


class OrderData(BaseModel):
    productId: Optional[int] = None
    quantity: float
    buyer: str
    buyerEmail: str
    productName: Optional[str] = ""
    productDescription: Optional[str] = ""
    productPrice: Optional[float] = 0
    productCurrency: Optional[str] = "USD"
    productMOQ: Optional[float] = 1
    productCountry: Optional[str] = ""
    productSeller: Optional[str] = "TAAVO Seller"


class PaymentData(BaseModel):
    orderId: int
    buyer: str
    buyerEmail: str
    amount: float
    currency: str = "USD"
    method: str


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    index_path = os.path.join(os.path.dirname(__file__), "index.html")

    if os.path.exists(index_path):
        return FileResponse(index_path)

    return {
        "name": "TAAVO",
        "message": "TAAVO Backend is running",
        "version": "3.0.0"
    }


# =========================================================
# STATUS
# =========================================================

@app.get("/api/status")
def status():
    return {
        "success": True,
        "status": "online",
        "service": "TAAVO Backend",
        "version": "3.0.0",
        "stage": "Payment MVP"
    }


@app.get("/api/test")
def test():
    return {
        "success": True,
        "message": "TAAVO API test successful",
        "version": "3.0.0"
    }


# =========================================================
# SIGNUP
# =========================================================

@app.post("/api/signup")
def signup(data: SignupData):

    email = data.email.strip().lower()

    if not data.name.strip() or not email or not data.password:
        return {
            "status": "error",
            "message": "All fields are required."
        }

    if email in users:
        return {
            "status": "error",
            "message": "An account with this email already exists."
        }

    role = data.role if data.role in ["Buyer", "Seller"] else "Buyer"

    user = {
        "name": data.name.strip(),
        "email": email,
        "role": role
    }

    users[email] = {
        **user,
        "password": data.password
    }

    return {
        "status": "success",
        "message": "TAAVO account created successfully!",
        "user": user
    }


# =========================================================
# LOGIN
# =========================================================

@app.post("/api/login")
def login(data: LoginData):

    email = data.email.strip().lower()
    user = users.get(email)

    if not user or user["password"] != data.password:
        return {
            "status": "error",
            "message": "Invalid email or password."
        }

    return {
        "status": "success",
        "message": "Login successful!",
        "user": {
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    }


# =========================================================
# BUYER REQUESTS
# =========================================================

@app.post("/api/buyer-requests")
def create_buyer_request(data: BuyerRequestData):

    request_id = len(buyer_requests) + 1

    request = {
        "id": request_id,
        "requirement": data.requirement.strip(),
        "quantity": data.quantity or "",
        "budget": data.budget or "",
        "currency": data.currency or "USD",
        "targetCountry": data.targetCountry or "",
        "status": "Pending",
        "replies": [],
        "createdAt": datetime.utcnow().isoformat() + "Z"
    }

    buyer_requests.append(request)

    return {
        "status": "success",
        "message": "Buyer request created successfully!",
        "request": request
    }


@app.get("/api/buyer-requests")
def get_buyer_requests():

    return {
        "status": "success",
        "requests": buyer_requests
    }


@app.post("/api/buyer-requests/reply")
def seller_reply(data: SellerReplyData):

    request = next(
        (item for item in buyer_requests if item["id"] == data.requestId),
        None
    )

    if not request:
        return {
            "status": "error",
            "message": "Buyer request not found."
        }

    message = data.message.strip()

    if not message:
        return {
            "status": "error",
            "message": "Reply message is required."
        }

    reply = {
        "sender": data.seller.strip() or "TAAVO Seller",
        "message": message,
        "createdAt": datetime.utcnow().isoformat() + "Z"
    }

    request["replies"].append(reply)
    request["status"] = "Seller Replied"

    return {
        "status": "success",
        "message": "Seller reply sent successfully!",
        "request": request
    }


# =========================================================
# PRODUCTS
# =========================================================

@app.post("/api/products")
def create_product(data: ProductData):

    product = {
        "id": len(products) + 1,
        "name": data.name.strip(),
        "description": data.description or "",
        "price": float(data.price),
        "currency": data.currency,
        "moq": float(data.moq),
        "country": data.country.strip(),
        "seller": data.seller.strip() or "Unknown Seller"
    }

    products.append(product)

    return {
        "status": "success",
        "message": "Product published successfully!",
        "product": product
    }


@app.get("/api/products")
def get_products():

    return {
        "status": "success",
        "products": products
    }


# =========================================================
# ORDERS
# =========================================================

@app.post("/api/orders")
def create_order(data: OrderData):

    if data.quantity <= 0:
        return {
            "status": "error",
            "message": "Order quantity must be greater than 0."
        }

    if not data.buyer.strip() or not data.buyerEmail.strip():
        return {
            "status": "error",
            "message": "Buyer account information is required."
        }

    product = None

    if data.productId is not None:

        product = next(
            (
                item
                for item in products
                if int(item["id"]) == int(data.productId)
            ),
            None
        )

    if not product and data.productName and data.productName.strip():

        new_product = {
            "id": len(products) + 1,
            "name": data.productName.strip(),
            "description": data.productDescription or "",
            "price": float(data.productPrice or 0),
            "currency": data.productCurrency or "USD",
            "moq": float(data.productMOQ or 1),
            "country": data.productCountry or "",
            "seller": data.productSeller or "TAAVO Seller"
        }

        products.append(new_product)
        product = new_product

    if not product:

        return {
            "status": "error",
            "message": "Product information is missing."
        }

    total = round(
        float(product["price"]) * float(data.quantity),
        2
    )

    order = {
        "id": len(orders) + 1,
        "productId": product["id"],
        "productName": product["name"],
        "seller": product["seller"],
        "buyer": data.buyer.strip(),
        "buyerEmail": data.buyerEmail.strip().lower(),
        "quantity": float(data.quantity),
        "unitPrice": float(product["price"]),
        "currency": product["currency"],
        "total": total,
        "status": "Pending",
        "paymentStatus": "Unpaid",
        "paymentId": None,
        "createdAt": datetime.utcnow().isoformat() + "Z"
    }

    orders.append(order)

    return {
        "status": "success",
        "message": "TAAVO order created successfully!",
        "order": order
    }


@app.get("/api/orders")
def get_orders():

    return {
        "status": "success",
        "orders": orders
    }


@app.get("/api/orders/{order_id}")
def get_order(order_id: int):

    order = next(
        (item for item in orders if item["id"] == order_id),
        None
    )

    if not order:
        return {
            "status": "error",
            "message": "Order not found."
        }

    return {
        "status": "success",
        "order": order
    }


# =========================================================
# PAYMENT
# =========================================================

@app.post("/api/payments")
def create_payment(data: PaymentData):

    order = next(
        (item for item in orders if item["id"] == data.orderId),
        None
    )

    if not order:
        return {
            "status": "error",
            "message": "Order not found."
        }

    if order["paymentStatus"] == "Paid":
        return {
            "status": "error",
            "message": "This order has already been paid."
        }

    if data.amount <= 0:
        return {
            "status": "error",
            "message": "Invalid payment amount."
        }

    allowed_methods = [
        "Card",
        "Bank Transfer",
        "Mobile Payment"
    ]

    if data.method not in allowed_methods:
        return {
            "status": "error",
            "message": "Invalid payment method."
        }

    payment_id = f"PAY-{len(payments) + 1:05d}"

    payment = {
        "id": payment_id,
        "orderId": data.orderId,
        "buyer": data.buyer.strip(),
        "buyerEmail": data.buyerEmail.strip().lower(),
        "amount": float(data.amount),
        "currency": data.currency,
        "method": data.method,
        "status": "Paid",
        "createdAt": datetime.utcnow().isoformat() + "Z"
    }

    payments.append(payment)

    order["paymentStatus"] = "Paid"
    order["paymentId"] = payment_id
    order["status"] = "Processing"

    return {
        "status": "success",
        "message": "Payment successful!",
        "payment": payment,
        "order": order
    }


@app.get("/api/payments")
def get_payments():

    return {
        "status": "success",
        "payments": payments
    }


@app.get("/api/payments/{payment_id}")
def get_payment(payment_id: str):

    payment = next(
        (item for item in payments if item["id"] == payment_id),
        None
    )

    if not payment:
        return {
            "status": "error",
            "message": "Payment not found."
        }

    return {
        "status": "success",
        "payment": payment
    }


# =========================================================
# STARTUP
# =========================================================

@app.on_event("startup")
async def startup_message():

    print("==========================================")
    print("TAAVO Backend started successfully")
    print("TAAVO API version: 3.0.0")
    print("Orders API: ENABLED")
    print("Payment API: ENABLED")
    print("POST /api/orders: ENABLED")
    print("GET  /api/orders: ENABLED")
    print("POST /api/payments: ENABLED")
    print("GET  /api/payments: ENABLED")
    print("==========================================")
