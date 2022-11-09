from fastapi import FastAPI, Header, Body, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from decouple import config
from models import favorites_models, error_models
from modules.jwt.jwt_module import JwtEncoder
import deta
import uuid

PROJECT_KEY = config("PROJECT_KEY")
MICROSERVICE_ACCESS_SECRET = config("MICROSERVICE_ACCESS_SECRET")
JWT_ALGORITHM="HS256"

deta = deta.Deta(PROJECT_KEY)
favoritesDB = deta.Base("favorites")

microservice_access_jwt_encoder = JwtEncoder(secret=MICROSERVICE_ACCESS_SECRET, algorithm=JWT_ALGORITHM)

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

def protect_route(microservice_access_token:str):
    if not microservice_access_jwt_encoder.validate_jwt(token=microservice_access_token):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")

@app.get(
    "/favorites",
    response_model=favorites_models.FavoritesModel,
    response_description="Returns favorites object with lists of product and component favorites",
    description="Get all favorites belonging to a user.",    
)
async def get_favorites_for_user(user_id: str = Header(alias="userId"), microservice_access_token:str = Header(alias="microserviceAccessToken")):
    protect_route(microservice_access_token)
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
async def create_favorites_obj_for_user(owner:favorites_models.FavoritesRequestModel, microservice_access_token:str = Header(alias="microserviceAccessToken")):
    protect_route(microservice_access_token)
    
    try:
        new_favorites_obj = {
            "component_ids":[],
            "product_ids":[]
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
            "description": "Error raised if database request fails."
        }},
    description="Adds an item to the favorites list of the user.",
)
async def adds_item_to_user_favorites_list(item_to_add:favorites_models.ToggleFavoriteModel, user_id: str = Header(alias="userId"), microservice_access_token:str = Header(alias="microserviceAccessToken")):
    protect_route(microservice_access_token)
    
    try:
        favorites_obj = favoritesDB.fetch({"key": user_id}).items[0]
    except Exception:
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
    except Exception:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Error while connecting to database")


@app.delete(
    "/favorites",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Deletes the favorites list of a user",
)
async def delete_favorites_obj_for_user(owner:favorites_models.FavoritesRequestModel, microservice_access_token:str = Header(alias="microserviceAccessToken")):
    protect_route(microservice_access_token)
   
    try:
        favoritesDB.delete(owner.key)
    except Exception:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.delete(
     "/favorites/items",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={503 :{
            "model": error_models.HTTPErrorModel,
            "description": "Error raised if database request fails."
        }},
    description="Removes an item from the favorites list of a user"
)
async def delete_item_from_favorites_for_user(item_to_remove:favorites_models.ToggleFavoriteModel, user_id: str = Header(alias="userId"), microservice_access_token:str = Header(alias="microserviceAccessToken")):
    protect_route(microservice_access_token)
    
    try:
        favorites_obj = favoritesDB.fetch({"key": user_id}).items[0]
    except Exception:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Error while connecting to database")
    
    try:
        
        if item_to_remove.item_type == "component":
            component_favorites = favorites_obj["component_ids"]
            try:
               component_favorites.remove(item_to_remove.id)
            except ValueError:
                return
            update = {"component_ids":component_favorites}

        elif item_to_remove.item_type == "product":
            product_favorites = favorites_obj["product_ids"]
            try:
                product_favorites.remove(item_to_remove.id)
            except ValueError:
                return
            update = {"product_ids":product_favorites}
        favoritesDB.update(update, user_id)

    except Exception:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Error while connecting to database")