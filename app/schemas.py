from fastapi import File, UploadFile
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class CreateRest(BaseModel):
    name: str = Field(..., min_length=1)
    address : str = Field(..., min_length=1)

    banner: str
    menuimage: str

    oname : str = Field(..., min_length=1)
    ophone : str = Field(...)
    email : EmailStr = Field(..., min_length=1)
    email2 : EmailStr = Field(..., min_length=1)
    password : str = Field(..., min_length=1)
    phone : str = Field(...)

class RestID(BaseModel):
    r_id : int

class ItemId(BaseModel):
    id : int

class CreateGroup(RestID):
    name:str = Field(..., min_length=1)

class ItemPrice(BaseModel):
    qty : str
    price : float

class CreateItem(RestID):
    g_id:int
    name:str = Field(..., min_length=1)
    desc:str
    image: str
    ordertype: int
    labels : list[int]

class CreateDefaultItem(CreateItem):
    def_price: float

class CreateVarietyItem(CreateItem):
    item_prices:List[ItemPrice]

class CreateLabel(BaseModel):
    name:str = Field(..., min_length=1)

class CreateExtra(RestID):
    name:str = Field(..., min_length=1)
    price: float

class User(BaseModel):
    name: str
    email: EmailStr
    phone: str

# class Extras(BaseModel):
#     id: int

class OrderItem(BaseModel):
    id: int
    size: int #0 for def price
    price: float
    qty: int
    extras: Optional[List[int]] = []

class PlaceOrder(BaseModel):
    rest_id : int
    items : List[OrderItem]
    amt : float
    order_by : User
    remarks: Optional[str]
    dine_in: bool
    remarks: Optional[str]

class OrderID(BaseModel):
    o_id : int

class ImageUpload(BaseModel):
    filename: str
    extension: str
    image_data: str

