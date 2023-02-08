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
date_format = "%Y-%m-%d"


class Reservation(BaseModel):
    name: str
    start_date: date
    end_date: date
    room_id: int


client = MongoClient(f"mongodb://{username}:{password}@mongo.exceed19.online:8443/?authMechanism=DEFAULT")

db = client["exceed08"]

collection = db["oak_hw_day3"]

app = FastAPI()


def room_available(room_id: int, start_date: str, end_date: str):
    query = {"room_id": room_id,
             "$or":
                 [{"$and": [{"start_date": {"$lte": start_date}}, {"end_date": {"$gte": start_date}}]},
                  {"$and": [{"start_date": {"$lte": end_date}}, {"end_date": {"$gte": end_date}}]},
                  {"$and": [{"start_date": {"$gte": start_date}}, {"end_date": {"$lte": end_date}}]}]
             }

    result = collection.find(query, {"_id": 0})
    list_cursor = list(result)

    return not len(list_cursor) > 0


@app.get("/reservation/by-name/{name}")
def get_reservation_by_name(name: str):
    search_name = collection.find({"name": name}, {"_id": False})
    all_name = list(search_name)
    return {"all_name": all_name}


@app.get("/reservation/by-room/{room_id}")
def get_reservation_by_room(room_id: int):
    search_room = collection.find({"room_id": room_id}, {"_id": False})
    all_room = list(search_room)
    return {"all_name": all_room}


@app.post("/reservation")
def reserve(reservation: Reservation):
    if reservation.room_id not in range(1, 11):
        raise HTTPException(status_code=400, detail=f"room id: {reservation.room_id} does not exist.")
    if reservation.start_date >= reservation.end_date:
        raise HTTPException(status_code=400, detail="Invalid date")
    if not room_available(reservation.room_id, reservation.start_date.strftime(date_format),
                          reservation.end_date.strftime(date_format)):
        raise HTTPException(status_code=400, detail="Room unavailable")
    reservation_data = {
        "name": f"{reservation.name}",
        "room_id": f"{reservation.room_id}",
        "start_date": f"{reservation.start_date.strftime(date_format)}",
        "end_date": f"{reservation.end_date.strftime(date_format)}"
    }
    collection.insert_one(reservation_data)
    return {"message": "Reservation complete"}


@app.put("/reservation/update")
def update_reservation(reservation: Reservation, new_start_date: date = Body(), new_end_date: date = Body()):
    if new_start_date >= new_end_date:
        raise HTTPException(status_code=400, detail="Invalid date")
    if not room_available(reservation.room_id, reservation.start_date.strftime(date_format),
                          reservation.end_date.strftime(date_format)):
        raise HTTPException(status_code=400, detail="Room unavailable")
    reservation_data = {
        "name": f"{reservation.name}",
        "room_id": f"{reservation.room_id}",
        "start_date": f"{reservation.start_date.strftime(date_format)}",
        "end_date": f"{reservation.end_date.strftime(date_format)}"
    }
    collection.update_one(reservation_data,
                          {"$set": {"start_date": f"{new_start_date}", "end_date": f"{new_end_date}"}}
                          )


@app.delete("/reservation/delete")
def cancel_reservation(reservation: Reservation):
    reservation_data = {
        "name": f"{reservation.name}",
        "room_id": f"{reservation.room_id}",
        "start_date": f"{reservation.start_date.strftime(date_format)}",
        "end_date": f"{reservation.end_date.strftime(date_format)}"
    }
    collection.delete_one(reservation_data)
    return {"message": "Reservation has been cancelled"}
