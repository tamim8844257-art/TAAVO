from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os

app = FastAPI(title="TAAVO", version="1.0.0")

# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Temporary in-memory data
# =========================

users = []
products = []
buyer_requests = []

# =========================
# Models
# =========================

class SignupData(BaseModel):
    name: str
    email: str
    password: str
    role: str


class LoginData(BaseModel):
    email: str
    password: str


class BuyerRequestData(BaseModel):
    requirement: str
    quantity: str
    budget: str
    currency: str
    targetCountry: str


class ProductData(BaseModel):
    name: str
    description: str
    price: float
    currency: str
    moq: int
    country: str
    seller: Optional[str] = "Unknown Seller"


# =========================
# HOME
# =========================

@app.get("/")
def home():
    index_path = os.path.join(os.path.dirname(__file__), "index.html")

    if os.path.exists(index_path):
        return FileResponse(index_path)

    return {
        "status": "success",
        "message": "TAAVO Backend is running!",
        "platform": "TAAVO - Trade Without Borders"
    }


# =========================
# STATUS
# =========================

@app.get("/api/status")
def status():
    return {
        "success": True,
        "message": "TAAVO API is working",
        "stage": "Foundation",
        "backend": "online"
    }


# =========================
# TEST
# =========================

@app.get("/api/test")
def test():
    return {
        "success": True,
        "message": "TAAVO connection test successful!"
    }


# =========================
# SIGN UP
# =========================

@app.post("/api/signup")
def signup(data: SignupData):

    for user in users:
        if user["email"].lower() == data.email.lower():
            return {
                "status": "error",
                "message": "Email already registered"
            }

    user = {
        "id": len(users) + 1,
        "name": data.name,
        "email": data.email,
        "password": data.password,
        "role": data.role
    }

    users.append(user)

    return {
        "status": "success",
        "message": "TAAVO account created successfully",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"]
        }
    }


# =========================
# LOGIN
# =========================

@app.post("/api/login")
def login(data: LoginData):

    for user in users:
        if (
            user["email"].lower() == data.email.lower()
            and user["password"] == data.password
        ):
            return {
                "status": "success",
                "message": "Login successful",
                "user": {
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"],
                    "role": user["role"]
                }
            }

    return {
        "status": "error",
        "message": "Invalid email or password"
    }


# =========================
# BUYER REQUEST
# =========================

@app.post("/api/buyer-requests")
def create_buyer_request(data: BuyerRequestData):

    request = {
        "id": len(buyer_requests) + 1,
        "requirement": data.requirement,
        "quantity": data.quantity,
        "budget": data.budget,
        "currency": data.currency,
        "targetCountry": data.targetCountry
    }

    buyer_requests.append(request)

    return {
        "status": "success",
        "message": "Buyer request created successfully",
        "request": request
    }


# =========================
# GET BUYER REQUESTS
# =========================

@app.get("/api/buyer-requests")
def get_buyer_requests():
    return {
        "status": "success",
        "requests": buyer_requests
    }


# =========================
# ADD PRODUCT
# =========================

@app.post("/api/products")
def create_product(data: ProductData):

    product = {
        "id": len(products) + 1,
        "name": data.name,
        "description": data.description,
        "price": data.price,
        "currency": data.currency,
        "moq": data.moq,
        "country": data.country,
        "seller": data.seller
    }

    products.append(product)

    return {
        "status": "success",
        "message": "Product published successfully",
        "product": product
    }


# =========================
# GET PRODUCTS
# =========================

@app.get("/api/products")
def get_products():
    return {
        "status": "success",
        "products": products
    }