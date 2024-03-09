import pytest
from httpx import AsyncClient
from starlette import status

pytestmark = pytest.mark.asyncio

admin_payments_url = "/api/v1/admin/payments/"
payments_url = "/api/v1/payments/"


async def test_get_payment(http_client: AsyncClient):
    payment_id = 1
    response = await http_client.get(payments_url + str(payment_id))
    assert response.status_code == status.HTTP_200_OK


async def test_missing_payment(http_client: AsyncClient):
    payment_id = 10001
    response = await http_client.get(payments_url + str(payment_id))
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    detail = response.json()["detail"]
    assert detail["code"] == 1001
    assert detail["message"] == "Payment not found"


async def test_get_user_payments(http_client: AsyncClient):
    response = await http_client.get(payments_url)
    assert response.status_code == status.HTTP_200_OK


async def test_get_all_payments(http_client: AsyncClient):
    response = await http_client.get(admin_payments_url)
    assert response.status_code == status.HTTP_200_OK
