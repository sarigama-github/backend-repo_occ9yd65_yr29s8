from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr


class Product(BaseModel):
    sku: str
    title: str
    description: str
    price: int = Field(ge=0)
    image: Optional[str] = None


class ContactInquiry(BaseModel):
    name: str
    email: EmailStr
    message: str
    language: str = Field(default="en")


class OrderItem(BaseModel):
    sku: str
    quantity: int = Field(ge=1)
    price: int = Field(ge=0)


class Order(BaseModel):
    items: List[OrderItem]
    customer: dict
    currency: str = Field(default="JPY")
    language: str = Field(default="en")
