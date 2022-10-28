from fastapi.testclient import TestClient
from decouple import config
from main import app
import uuid

def test_get_favorites_endpoint_returns_favorites_for_user():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    expected_favorites_obj = {
        "favoritesListId":"test_favorites_list_id",
        "ownerId":TEST_USER_ID,
        "componentIds":["546c08d7-539d-11ed-a980-cd9f67f7363d","546c08da-539d-11ed-a980-cd9f67f7363d"],
        "productIds":[]
    }
    #ACT
    response = client.get("/favorites",headers={"userId":TEST_USER_ID})
    #ASSERT
    assert response.status_code == 200
    assert response.json() == expected_favorites_obj


def test_post_favorites_endpoint_creates_favorites_obj():
    #ARRANGE
    client = TestClient(app)
    random_user_id = str(uuid.uuid1())
    expected_favorites_obj = {
        "ownerId":random_user_id,
        "componentIds":[],
        "productIds":[]
    }
    #ACT
    response = client.post("/favorites",json={"userId":random_user_id})
    #ASSERT
    assert response.status_code == 201
    assert response.json() >= expected_favorites_obj