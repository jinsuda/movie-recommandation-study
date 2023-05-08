from fastapi import FastAPI, Depends, Path, HTTPException
from pydantic import BaseModel
from database import engineconn
from models import Test

app = FastAPI()

engine = engineconn()
session = engine.sessionmaker()

class Item(BaseModel):
    name : str
    phoneNumber : int
    email : str
    Korean : int
    Math : int
    English : int
    
@app.get("/")
async def first_get():
    example = session.query(Test).all()
    return example

@app.post("/insert")
async def insert(item : Item):
    addMemo = Test(lastname=item.name.split()[0],firstname=item.name.split()[1], phoneNumber=item.phoneNumber, email=item.email, Korean=item.Korean, Math=item.Math, English=item.English )
    session.add(addMemo)
    session.commit()
    return item