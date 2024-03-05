import pytest
import os
from starlette import status
import json
import asyncpg


pytestmark = pytest.mark.anyio

base_url = os.getenv("BILLING_API_URL", "http://localhost:8000/api/v1/")
features_url = base_url + "/features"
admin_features_url = base_url + "admin/features/"


# TODO нужна фикстура, добавляющая строку в таблицу
async def test_get_feature():
    pass


# TODO нужна фикстура, добавляющая строку в таблицу
async def test_get_features():
    pass


async def test_create_feature(http_client):
    response = await http_client.request(
        "POST",
        admin_features_url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(
            {
                "name": "Test Feature",
                "description": "Test Feature Description",
                "available_entities": [],
            }
        ),
    )
    assert response.status_code == status.HTTP_201_CREATED


async def test_update_feature(http_client):
    response = await http_client.request(
        "PUT",
        admin_features_url + "{id}",
        params={"feature_id": 999999},
        headers={"Content-Type": "application/json"},
        data=json.dumps({"name": "New Test Feature"}),
    )
    assert response.status_code == status.HTTP_200_OK


async def test_delete_feature(http_client):
    response = await http_client.request(
        "DELETE",
        admin_features_url + "{id}",
        params={"feature_id": 999999},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["success"] is True
