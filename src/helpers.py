import logging
from datetime import datetime
from functools import wraps

import aiohttp
from sqlalchemy import exc
from sqlmodel.ext.asyncio.session import AsyncSession

from src.core.config import settings
from src.core.exceptions import ServiceError

logger = logging.getLogger(__name__)


def catch_sa_errors(func):
    @wraps(func)
    async def wrapper(cls, *args, session: AsyncSession, **kwargs):
        try:
            return await func(cls, *args, session=session, **kwargs)
        except exc.SQLAlchemyError as error:
            logger.exception(error)
            await session.rollback()
            raise ServiceError

    return wrapper


async def send_notification(
    user_id: str, event_type: str, data: dict = None, object_id: str = None,
):
    """
    {
        "content":
            {
                "userId": "b63e0639-5ff5-4435-831f-19f6a5548d25",
                "eventTimestamp": 1707164125.6069813,
                "eventType": "subscription is active",
                "objectId": "b63e0639-5ff5-4435-831f-19f6a5548d25",
                "data": {"expired_at": "2023-01-01T00:00:00"}
            },
        "content_related_users": ["b63e0639-5ff5-4435-831f-19f6a5548d25"],
        "content_type": "billing"
    },
    {
        "content":
            {
                "userId": "b63e0639-5ff5-4435-831f-19f6a5548d25",
                "eventTimestamp": 1707164125.6069813,
                "eventType": "subscription expired",
                "objectId": "b63e0639-5ff5-4435-831f-19f6a5548d25",
                "data": {"expired_at": "2023-01-01T00:00:00"}
            },
        "content_related_users": ["b63e0639-5ff5-4435-831f-19f6a5548d25"],
        "content_type": "billing"
    },
    {
        "content":
            {
                "userId": "b63e0639-5ff5-4435-831f-19f6a5548d25",
                "eventTimestamp": 1707164125.6069813,
                "eventType": "subscription paused",
                "objectId": "b63e0639-5ff5-4435-831f-19f6a5548d25",
                "data": {"paused_until": "2023-01-01T00:00:00"}
            },
        "content_related_users": ["b63e0639-5ff5-4435-831f-19f6a5548d25"],
        "content_type": "billing"
    },
    {
        "content":
            {
                "userId": "b63e0639-5ff5-4435-831f-19f6a5548d25",
                "eventTimestamp": 1707164125.6069813,
                "eventType": "subscription cancelled",
                "objectId": "b63e0639-5ff5-4435-831f-19f6a5548d25",
                "data": {}
            },
        "content_related_users": ["b63e0639-5ff5-4435-831f-19f6a5548d25"],
        "content_type": "billing"
    },
    {
        "content":
            {
                "userId": "b63e0639-5ff5-4435-831f-19f6a5548d25",
                "eventTimestamp": 1707164125.6069813,
                "eventType": "subscription prolonged",
                "objectId": "b63e0639-5ff5-4435-831f-19f6a5548d25",
                "data": {"expired_at": "2023-01-01T00:00:00"}
            },
        "content_related_users": ["b63e0639-5ff5-4435-831f-19f6a5548d25"],
        "content_type": "billing"
    },
    {
        "content":
            {
                "userId": "b63e0639-5ff5-4435-831f-19f6a5548d25",
                "eventTimestamp": 1707164125.6069813,
                "eventType": "unsuccessful payment",
                "objectId": "b63e0639-5ff5-4435-831f-19f6a5548d25",
                "data": {}
            },
        "content_related_users": ["b63e0639-5ff5-4435-831f-19f6a5548d25"],
        "content_type": "billing"
    },
    {
        "content":
            {
                "userId": "b63e0639-5ff5-4435-831f-19f6a5548d25",
                "eventTimestamp": 1707164125.6069813,
                "eventType": "successful payment",
                "objectId": "b63e0639-5ff5-4435-831f-19f6a5548d25",
                "data": {"amount": 100, "currency": "USD"}
            },
        "content_related_users": ["b63e0639-5ff5-4435-831f-19f6a5548d25"],
        "content_type": "billing"
    },
    :return:
    """
    data = {
        "content": {
            "userId": user_id,
            "eventTimestamp": datetime.utcnow().timestamp(),
            "eventType": event_type,
            "data": data,
            "objectId": object_id
        },
        "content_related_users": [user_id],
        "content_type": "billing",
    }

    try:
        async with aiohttp.ClientSession() as session:
            await session.post(f"{settings.notification_api_url}", json=data)
    except aiohttp.ClientError as e:
        logger.exception(e)


async def send_analytics(user_id: str, event_value: str, event_name: str = "subscription"):
    """
    {
        "event_name": "subscription",
        "event_value": "active", # active, paused, cancelled, expired
        "event_amount": 1,
        "event_sender": "billing",
        "event_timestamp": 1707164125.6069813,
        "user_id": "b63e0639-5ff5-4435-831f-19f6a5548d25",
        "event_metadata": {},
    }
    :return:
    """
    data = {
        "event_name": event_name,
        "event_value": event_value,
        "event_amount": 1,
        "event_sender": "billing",
        "event_timestamp": datetime.utcnow().timestamp(),
        "user_id": user_id,
        "event_metadata": {},
    }
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(f"{settings.analytics_api_url}", json=data)
    except aiohttp.ClientError as e:
        logger.exception(e)
