from fastapi import FastAPI, HTTPException, Body
from datetime import date
from pymongo import MongoClient
from pydantic import BaseModel
from dotenv import load_dotenv
import os

DATABASE_NAME = "hotel"
COLLECTION_NAME = "reservation"
load_dotenv(".env")
username = os.getenv("username")
password = os.getenv("password")


class Reservation(BaseModel):
    name : str
    start_date: str
    end_date: str
    room_id: int


client = MongoClient(f"mongodb://{username}:{password}@mongo.exceed19.online:8443/?authMechanism=DEFAULT")

db = client["exceed08"]

collection = db["oak_hw_day3"]

app = FastAPI()


def room_available(room_id: int, start_date: str, end_date: str):
    query={"room_id": room_id,
           "$or": 
                [{"$and": [{"start_date": {"$lte": start_date}}, {"end_date": {"$gte": start_date}}]},
                 {"$and": [{"start_date": {"$lte": end_date}}, {"end_date": {"$gte": end_date}}]},
                 {"$and": [{"start_date": {"$gte": start_date}}, {"end_date": {"$lte": end_date}}]}]
            }
    
    result = collection.find(query, {"_id": 0})
    list_cursor = list(result)

    return not len(list_cursor) > 0








@app.get("/reservation/by-name/{name}")
def get_reservation_by_name(name:str):
    pass

@app.get("/reservation/by-room/{room_id}")
def get_reservation_by_room(room_id: int):
    pass

@app.post("/reservation")
def reserve(reservation : Reservation):
    room = room_available(reservation.room_id, reservation.start_date, reservation.end_date)
    if room:
        reservation_data ={
                "name": f"{reservation.name}",
                "room_id": f"{reservation.room_id}",
                "start_date": f"{reservation.start_date}",
                "end_date": f"{reservation.end_date}"
            }
        collection.insert_one(reservation_data)
        return {"message": "reservation is complete"}
    else:
        return {"message": "reservation cannot be proceeded"}

@app.put("/reservation/update")
def update_reservation(reservation: Reservation, new_start_date: date = Body(), new_end_date: date = Body()):
    pass

@app.delete("/reservation/delete")
def cancel_reservation(reservation: Reservation):
    pass

