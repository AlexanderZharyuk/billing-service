import pytest
import os
from starlette import status
import json

pytestmark = pytest.mark.anyio

base_url = os.getenv("BILLING_URL", "http://localhost:8000/api/v1")
admin_payments_url = base_url + "/admin/payments/"
payments_url = base_url + "/payments/"


# TODO нужна фикстура, добавляющая строку в таблицу
async def test_get_payment(http_client):
    pass


# TODO нужна фикстура, добавляющая строку в таблицу
async def test_get_payments(http_client):
    pass
