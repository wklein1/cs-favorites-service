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


@app.post(
    "/favorites/items",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={409 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if item is already in favorites list."
        },
        503 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if database requests fail."
        }},
    description="Adds an item to the favorites list of the user.",
)
async def adds_item_to_user_favorites_list(item_to_add:favorites_models.ToggleFavoriteModel, user_id: str = Header(alias="userId")):
    try:
        favorites_obj = favoritesDB.fetch({"key": user_id}).items[0]
    except Exception as ex:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Error while connecting to database")
    
    if item_to_add.item_type == "component":
        if item_to_add.id in favorites_obj["component_ids"]:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Item is already in favorites list.")
        update = { "component_ids":favoritesDB.util.append(item_to_add.id)}
        
    elif item_to_add.item_type == "product":
        if item_to_add.id in favorites_obj["product_ids"]:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Item is already in favorites list.")
        update = { "product_ids":favoritesDB.util.append(item_to_add.id)}
    
    try:
        updated_favorites_obj = favoritesDB.update(update, user_id)
    except Exception as ex:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Error while connecting to database")


@app.delete(
     "/favorites",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Deletes the favorites list of a user",
)
async def delete_favorites_obj_for_user(owner:favorites_models.FavoritesRequestModel):
    favoritesDB.delete(owner.key)