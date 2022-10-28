from fastapi.testclient import TestClient
from decouple import config
from main import app
import uuid

def test_get_favorites_endpoint_returns_favorites_for_user():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    expected_favorites_obj = {
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
    response = client.post("/favorites",json={"ownerId":random_user_id})
    #ASSERT
    assert response.status_code == 201
    assert response.json().items() >= expected_favorites_obj.items()
    #CLEANUP
    client.delete("/favorites",json={"ownerId":random_user_id})


def test_post_favorites_endpoint_fails_creating_existing_favorites_obj():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    expected_error = {
        "detail": "User already has a favorites list."
    }
    #ACT
    response = client.post("/favorites",json={"ownerId":TEST_USER_ID})
    #ASSERT
    assert response.status_code == 409
    assert response.json() == expected_error

def test_post_favorite_endpoint_adds_product_favorite_to_list():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    expected_favorites_obj = {
        "ownerId":TEST_USER_ID,
        "componentIds":["546c08d7-539d-11ed-a980-cd9f67f7363d","546c08da-539d-11ed-a980-cd9f67f7363d"],
        "productIds":["29f6f518-53a8-11ed-a980-cd9f67f7363d"]
    }
    #ACT
    response = client.post("/favorites/items",json={"id":"29f6f518-53a8-11ed-a980-cd9f67f7363d","itemType":"product"},headers={"userId":TEST_USER_ID})
    #ASSERT
    assert response.status_code == 204
    #CLEANUP
    client.delete("/favorites/items",json={"id":"29f6f518-53a8-11ed-a980-cd9f67f7363d","itemType":"product"}, headers={"userId":TEST_USER_ID})


def test_post_favorite_endpoint_adds_component_favorite_to_list():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    expected_favorites_obj = {
        "ownerId":TEST_USER_ID,
        "componentIds":["546c08d7-539d-11ed-a980-cd9f67f7363d","546c08da-539d-11ed-a980-cd9f67f7363d","546c08de-539d-11ed-a980-cd9f67f7363d"],
        "productIds":[]
    }
    #ACT
    response = client.post("/favorites/items",json={"id":"546c08de-539d-11ed-a980-cd9f67f7363d","itemType":"component"},headers={"userId":TEST_USER_ID})
    #ASSERT
    assert response.status_code == 204
    #CLEANUP
    client.delete("/favorites/items",json={"id":"546c08de-539d-11ed-a980-cd9f67f7363d","itemType":"component"}, headers={"userId":TEST_USER_ID})


def test_post_favorite_endpoint_fails_to_add_already_added_product_to_favorites():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    expected_error = {
        "detail": "Item is already in favorites list."
    }
    client.post("/favorites/items",json={"id":"29f6f518-53a8-11ed-a980-cd9f67f7363d","itemType":"product"},headers={"userId":TEST_USER_ID})
    #ACT
    response = client.post("/favorites/items",json={"id":"29f6f518-53a8-11ed-a980-cd9f67f7363d","itemType":"product"},headers={"userId":TEST_USER_ID})
    #ASSERT
    assert response.status_code == 409
    assert response.json() == expected_error

def test_post_favorite_endpoint_fails_to_add_already_added_component_to_favorites():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    expected_error = {
        "detail": "Item is already in favorites list."
    }
    #ACT
    response = client.post("/favorites/items",json={"id":"546c08d7-539d-11ed-a980-cd9f67f7363d","itemType":"component"},headers={"userId":TEST_USER_ID})
    #ASSERT
    assert response.status_code == 409
    assert response.json() == expected_error
    

def test_delete_favorites_endpoint():
    #ARRANGE
    client = TestClient(app)
    random_user_id = str(uuid.uuid1())
    expected_favorites_obj = {
        "ownerId":random_user_id,
        "componentIds":[],
        "productIds":[]
    }
    client.post("/favorites",json={"ownerId":random_user_id})
    #ACT
    response = client.delete("/favorites",json={"ownerId":random_user_id})
    #ASSERT
    assert response.status_code == 204


def test_delete_favorite_endpoint_deletes_product_favorite():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    client.post("/favorites/items",json={"id":"29f6f518-53a8-11ed-a980-cd9f67f7363d","itemType":"product"},headers={"userId":TEST_USER_ID})
    #ACT
    response = client.delete("/favorites/items",json={"id":"29f6f518-53a8-11ed-a980-cd9f67f7363d","itemType":"product"}, headers={"userId":TEST_USER_ID})
    #ASSERT
    assert response.status_code == 204

def test_delete_favorite_endpoint_deletes_component_favorite():
    #ARRANGE
    client = TestClient(app)
    TEST_USER_ID = config("TEST_USER_ID")
    client.post("/favorites/items",json={"id":"546c08de-539d-11ed-a980-cd9f67f7363d","itemType":"component"},headers={"userId":TEST_USER_ID})
    #ACT
    response = client.delete("/favorites/items",json={"id":"546c08de-539d-11ed-a980-cd9f67f7363d","itemType":"component"}, headers={"userId":TEST_USER_ID})
    #ASSERT
    assert response.status_code == 204