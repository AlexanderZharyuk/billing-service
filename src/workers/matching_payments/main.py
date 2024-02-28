import asyncio
import uuid
import var_dump as vd

from yookassa import Configuration, Settings, Payment
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text

from src.core.config import settings
from src.workers.helpers import session_injection


@session_injection
async def test(session: AsyncSession = None):
    #ToDo: for future
    """sql = text("SELECT * FROM templates")
    result = await session.exec(sql)
    return list(result.scalars())"""
    """payment = Payment.create({
        "amount": {
            "value": "100.00",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://www.example.com/return_url"
        },
        "capture": True,
        "description": "Заказ №2"
    }, uuid.uuid4())"""
    params = {
        "status": "succeeded",
        "created_at.gte": "2020-02-27T00:00:00.000Z",   # Созданы начиная с 2020-08-08
    }
    payment = Payment.list(params)
    """
    payment = Payment.create({
        "amount": {
            "value": "122.22",
            "currency": "RUB"
        },
        "capture": True,
        "payment_method_id": "2d6fd262-000f-5000-9000-1d53fbcaaf00",
        "description": "Заказ №37"
    })"""
    """payment = Payment.create({
        "amount": {
            "value": "2.00",
            "currency": "RUB"
        },
        "payment_method_data": {
            "type": "bank_card"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://www.example.com/return_url"
        },
        "capture": True,
        "description": "Заказ №3",
        "save_payment_method": True
    })"""
    return vd.var_dump(payment)


async def main():
    Configuration.configure(settings.shop_id, settings.shop_key)
    first = await test()
    print(f"func test1 execute: {first}\nfunc test2 execute: {first}")
    #ToDo: for future
    """while True:
        first = await test()
        print(f"func test1 execute: {first}\nfunc test2 execute: {first}")
        await asyncio.sleep(1)"""


if __name__ == "__main__":
    asyncio.run(main())
