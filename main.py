from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

products = []


@app.get("/api/status")
def status():
    return {
        "status": "online",
        "message": "TAAVO Backend is running"
    }


@app.post("/api/products")
def create_product(product: dict):
    products.append(product)

    return {
        "success": True,
        "product": product
    }


@app.get("/api/products")
def get_products():
    return {
        "success": True,
        "products": products
    }