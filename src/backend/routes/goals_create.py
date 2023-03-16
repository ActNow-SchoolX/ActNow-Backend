from fastapi import FastAPI
from typing import Optional
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.backend.database import engine

app = FastAPI()
Base = declarative_base()


class GoalsEntity(Base):
    __tablename__ = "goal"
    goal_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    price = Optional[Column(int)]
    date = Optional[Column(int)]


Session = sessionmaker(bind=engine)
session = Session()


@app.post("/goal_create")
async def create_entity(name: str, description: str, price: int, date: int):
    entity = GoalsEntity(name=name, description=description, cost=price, date=date)
    session.add(entity)
    session.commit()
    return {"message": "Entity created successfully"}
