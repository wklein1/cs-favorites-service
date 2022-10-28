from fastapi import FastAPI, Header, Body, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from decouple import config
from models import favorites_models, error_models
import deta
import uuid

PROJECT_KEY = config("PROJECT_KEY")

deta = deta.Deta(PROJECT_KEY)
favoritesDB = deta.Base("favorites")

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.get(
    "/favorites",
    response_model=favorites_models.FavoritesModel,
    response_description="Returns favorites object with lists of product and component favorites",
    description="Get all favorites belonging to a user.",    
)
async def get_favorites_for_user(user_id: str = Header(alias="userId")):
    return favoritesDB.fetch({"key": user_id}).items[0]


@app.post(
    "/favorites",
    status_code=status.HTTP_201_CREATED,
    response_model=favorites_models.FavoritesModel,
    response_description="Returns created favorites list",
    responses={409 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if user already has a favorites list."
        }},
    description="Create a new favorites list for a user",
)
async def create_favorites_obj_for_user(owner:favorites_models.FavoritesRequestModel):
    try:
        new_favorites_obj = {
            "componentIds":[],
            "productIds":[]
        }
        new_favorites_obj["key"] = owner.key
        favorites_obj = favoritesDB.insert(new_favorites_obj)
    except Exception as ex:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already has a favorites list.")
    return favorites_obj