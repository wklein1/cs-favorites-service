from fastapi.testclient import TestClient
from decouple import config
from main import app

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
    assert expected_favorites_obj == response.json()