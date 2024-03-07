from typing import Annotated

from fastapi import Depends

from src.v1.webhooks.services.yookassa import YooKassaWebhookService, get_yookassa_webhook_service


YooKassaWebhookService = Annotated[YooKassaWebhookService, Depends(get_yookassa_webhook_service)]
