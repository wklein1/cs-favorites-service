from models.custom_base_model import CustomBaseModel
from pydantic import Field

class FavoritesModel(CustomBaseModel):
    key: str = Field(alias="favoritesListId")
    owner_id: str
    component_ids: list[str]
    product_ids: list[str]

    def __getitem__(self, item):
        return getattr(self, item)

class ToggleFavoriteModel(CustomBaseModel):
    owner_id: str
    to_favorites_id: str