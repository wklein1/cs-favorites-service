from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from decouple import config
from models import favorites_models
import deta

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
    return favoritesDB.fetch({"owner_id": user_id}).items[0]
