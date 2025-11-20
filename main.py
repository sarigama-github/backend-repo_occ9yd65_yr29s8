import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Any
from bson import ObjectId

from schemas import ContactInquiry, Order
from database import db, create_document, get_documents

app = FastAPI(title="Global Card Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ObjectIdEncoder:
    @staticmethod
    def encode(doc: Any):
        if isinstance(doc, list):
            return [ObjectIdEncoder.encode(d) for d in doc]
        if isinstance(doc, dict):
            new_doc = {}
            for k, v in doc.items():
                if isinstance(v, ObjectId):
                    new_doc[k] = str(v)
                elif isinstance(v, list) or isinstance(v, dict):
                    new_doc[k] = ObjectIdEncoder.encode(v)
                else:
                    new_doc[k] = v
            return new_doc
        return doc


@app.get("/")
def read_root():
    return {"message": "Global Card Backend running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set",
        "database_name": "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["connection_status"] = "Connected"
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response


# Sample products as fallback if DB is empty
SAMPLE_PRODUCTS = [
    {
        "sku": "HIDE-PRM-210",
        "title": "HIDE Handmade Gyuto 210mm",
        "description": "Gyuto chef knife forged by artisan Shuichi Isayazaka. Aogami super core, stainless clad.",
        "price": 38500,
        "category": "Knife",
        "in_stock": True,
        "image": "/knife-gyuto.jpg",
    },
    {
        "sku": "HIDE-PET-150",
        "title": "HIDE Petty 150mm",
        "description": "Compact petty knife for precise work. Hand-ground, octagonal handle.",
        "price": 19800,
        "category": "Knife",
        "in_stock": True,
        "image": "/knife-petty.jpg",
    },
]


@app.get("/api/products")
def list_products():
    try:
        docs = []
        if db is not None:
            docs = get_documents("product")
        if not docs:
            return SAMPLE_PRODUCTS
        return ObjectIdEncoder.encode(docs)
    except Exception:
        # Fallback to sample data if db not available
        return SAMPLE_PRODUCTS


@app.post("/api/contact")
def submit_contact(inquiry: ContactInquiry):
    try:
        if db is None:
            # Accept even without DB, simulate success
            return {"status": "ok", "stored": False}
        _id = create_document("contactinquiry", inquiry)
        return {"status": "ok", "id": _id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/orders")
def create_order(order: Order):
    try:
        if db is None:
            return {"status": "ok", "stored": False, "total": order.total}
        _id = create_document("order", order)
        return {"status": "ok", "id": _id, "total": order.total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
