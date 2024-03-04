import pytest
import os
from starlette import status
import src.v1.features.models as models


pytestmark = pytest.mark.anyio
base_url = os.getenv("BILLING_API_URL", "http://localhost:8000/api/v1/")
features_url = base_url + "/features"


async def test_list_features(http_client):
    response = await http_client.request(
        "GET",
        features_url)
    assert response.status_code == status.HTTP_200_OK


async def test_get_feature():
    pass


async def test_create_feature():
    pass


async def test_update():
    pass


async def test_delete():
    pass