import logging

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from yookassa.domain.notification import WebhookNotification

from src.v1.webhooks.services import YooKassaWebhookService


router = APIRouter(prefix="/webhooks", tags=["Webhooks"])
logger = logging.getLogger(__name__)


@router.post(
    "/yookassa",
    summary="Получить информацию о статусе платежа YooKassa.",
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="Получить информацию о статусе платежа YooKassa.",
)
async def status_payment_yookassa(
    data: dict,
    service: YooKassaWebhookService = YooKassaWebhookService,
) -> JSONResponse:
    notification_object = WebhookNotification(data)
    event = notification_object.event

    match event:
        case "payment.succeeded":
            await service.activate_subscription(notification_object)
        case "refund.succeeded":
            await service.disable_subscription(notification_object)

    return JSONResponse(status_code=200, content={"received": True})
