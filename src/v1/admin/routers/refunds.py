from fastapi import APIRouter, status

from src.models import BaseResponseBody
from src.v1.payment_providers.models import PaymentProviderRefundParams
from src.v1.refunds.models import (
    RefundReasonCreate, SingleRefundReasonResponse, RefundTicketStatusEnum
)
from src.v1.refunds.service import (
    PostgresRefundReasonsService, PaymentProviderServiceForRefunds, PostgresRefundsService
)

router = APIRouter(prefix="/refunds", tags=["Refunds Admin"])


@router.post(
    "/reasons",
    summary="Создать причину для возврата",
    response_model=SingleRefundReasonResponse,
    status_code=status.HTTP_201_CREATED,
    description="Создать причину для возврата.",
)
async def create_refund_reason(
    data: RefundReasonCreate,
    service: PostgresRefundReasonsService = PostgresRefundReasonsService,
) -> SingleRefundReasonResponse:
    refund_reason = await service.create(data)
    return SingleRefundReasonResponse(data=refund_reason)


@router.post(
    "/",
    summary="Оформить возврат",
    response_model=BaseResponseBody,
    status_code=status.HTTP_201_CREATED,
    description="Оформить возврат.",
)
async def make_refund(
    data: PaymentProviderRefundParams,
    service: PaymentProviderServiceForRefunds = PaymentProviderServiceForRefunds,
) -> BaseResponseBody:
    refund = await service.make_refund(data)
    return BaseResponseBody(data=refund)


@router.get(
    "/",
    summary="Посмотреть запросы на возврат",
    response_model=BaseResponseBody,
    status_code=status.HTTP_200_OK,
    description="Посмотреть запросы на возврат",
)
async def get_tickets(
    only_open: bool = True,
    service: PostgresRefundsService = PostgresRefundReasonsService,
) -> BaseResponseBody:
    filter_ = None
    if only_open:
        filter_ = {"status": RefundTicketStatusEnum.OPEN}
    refunds = await service.get_all(filter_)
    return BaseResponseBody(data=refunds)


@router.delete(
    "/{ticket_id}",
    summary="Удалить запрос на возврат",
    response_model=BaseResponseBody,
    status_code=status.HTTP_200_OK,
    description="Удалить запрос на возврат",
)
async def delete_ticket(
    ticket_id: int,
    service: PostgresRefundsService = PostgresRefundReasonsService,
) -> BaseResponseBody:
    await service.delete(ticket_id)
    return BaseResponseBody(data={"success": True})
