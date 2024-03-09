import json

import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio

admin_features_url = "/api/v1/admin/features/"
features_url = "/api/v1/features/"


async def test_get_feature(http_client: AsyncClient):
    expected_data = "First Feature"
    feature_id = 1
    response = await http_client.get(features_url + str(feature_id))
    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"]["name"]
    assert data == expected_data


async def test_get_user_features(http_client: AsyncClient):
    expected_data = 3
    response = await http_client.get(features_url)
    data = len(response.json()["data"])
    assert response.status_code == status.HTTP_200_OK
    assert data == expected_data


async def test_create_feature(http_client: AsyncClient):
    response = await http_client.post(
        admin_features_url,
        headers={"Content-Type": "application/json"},
        json={
            "name": "Test Feature",
            "description": "Create Test Feature",
            "available_entities": [],
        },
    )
    assert response.status_code == status.HTTP_201_CREATED


async def test_update_feature(http_client: AsyncClient):
    feature_id = 1
    body = {"name": "Archive feature"}
    response = await http_client.patch(admin_features_url + str(feature_id), json=body)
    assert response.status_code == status.HTTP_200_OK


async def test_delete_feature(http_client: AsyncClient):
    feature_id = 1
    response = await http_client.delete(admin_features_url + str(feature_id))
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["success"] is True
