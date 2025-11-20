from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from schemas import Product, ContactInquiry, Order
from database import create_document, get_documents, get_db

app = FastAPI(title="HIDE Atelier API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


SAMPLE_PRODUCTS: List[dict] = [
    {
        "sku": "GYU210-AOGAMI",
        "title": "Gyuto 210mm — Aogami #2",
        "description": "Balanced, all-purpose chef's knife. Octagonal handle.",
        "price": 32000,
        "image": "/knife-hero.jpg",
    },
    {
        "sku": "PETTY135-SLD",
        "title": "Petty 135mm — Stainless clad",
        "description": "Compact precision for fruit and garnish. Stainless clad carbon core.",
        "price": 16000,
        "image": "/knife-hero.jpg",
    },
    {
        "sku": "SANTOKU180-VG10",
        "title": "Santoku 180mm — VG10",
        "description": "Daily driver for home kitchens. Easy maintenance.",
        "price": 21000,
        "image": "/knife-hero.jpg",
    },
    {
        "sku": "NAKIRI165-AOGAMI",
        "title": "Nakiri 165mm — Aogami #2",
        "description": "Thin, nimble vegetable specialist.",
        "price": 19000,
        "image": "/knife-hero.jpg",
    },
]


@app.get("/")
async def root():
    return {"message": "HIDE Atelier API running"}


@app.get("/test")
async def test():
    db = get_db()
    return {
        "backend": "ok",
        "database": "connected" if db is not None else "not_configured",
        "database_url": "set" if db is not None else "not_set",
        "database_name": getattr(db, "name", None) if db is not None else None,
        "connection_status": "ok" if db is not None else "skipped",
        "collections": [],
    }


@app.get("/api/products")
async def get_products():
    docs = await get_documents("product", {}, limit=20)
    if docs:
        # Normalize Mongo docs to API shape
        out = []
        for d in docs:
            out.append({
                "sku": d.get("sku"),
                "title": d.get("title"),
                "description": d.get("description"),
                "price": d.get("price", 0),
                "image": d.get("image"),
                "_id": str(d.get("_id")),
            })
        return out
    return SAMPLE_PRODUCTS


@app.post("/api/contact")
async def post_contact(payload: ContactInquiry):
    data = payload.model_dump()
    inserted_id = await create_document("contactinquiry", data)
    return {"status": "ok", "id": str(inserted_id) if inserted_id else None}


@app.post("/api/orders")
async def post_orders(payload: Order):
    data = payload.model_dump()
    if not data.get("items"):
        raise HTTPException(status_code=400, detail="No items provided")
    inserted_id = await create_document("order", data)
    return {"status": "ok", "id": str(inserted_id) if inserted_id else None}
