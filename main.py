
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated
from database import engine, SessionLocal
from pydantic import BaseModel
import models

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

class ItemBase(BaseModel):
    name: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(item: ItemBase, db: db_dependency):
    try:
        db_item = models.Item(**item.dict())
        db.add(db_item)
        db.commit()
        return {"message": "Item created successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    
@app.get("/items/")
async def read_items(db: db_dependency):
    db_items = db.query(models.Item).all()
    return [{"id": item.id, "item": item.name} for item in db_items]


@app.get("/items/{item_id}")
async def read_item(item_id: int, db: db_dependency):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return {"id": db_item.id, "item": db_item.name}

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: ItemBase, db: db_dependency):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    db_item.name = item.name
    db.commit()
    return {"message": "Item updated successfully"}

@app.delete("/items/{item_id}")
async def delete_item(item_id: int, db: db_dependency):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted successfully"}