from fastapi import APIRouter, status, Depends, Path

from src.v1.refunds.models import (
    RefundCreate,
    RefundReasonCreate,
    SingleRefundResponse,
    SeveralRefundsResponse,
    SingleRefundReasonResponse,
    SeveralRefundReasonsResponse
)
from src.v1.refunds.service import PostgresRefundsService, PostgresRefundsService, PostgresRefundReasonsService


router = APIRouter(prefix="/refunds", tags=["Refunds"])


@router.get(
    "/reasons",
    summary="Получить причины для возвраата",
    response_model=SeveralRefundReasonsResponse,
    status_code=status.HTTP_200_OK,
    description="Получить причины для возвраата",
)
async def get_refund_reasons(
    service: PostgresRefundReasonsService = PostgresRefundsService,
) -> SeveralRefundReasonsResponse:
    reasons = await service.get_all()
    return SeveralRefundReasonsResponse(data=reasons)


@router.post(
    "/",
    summary="Запросить рефанд",
    response_model=SingleRefundResponse,
    status_code=status.HTTP_200_OK,
    description="Запросить возврат средств.",
)
async def make_refund_ticket(
    data: RefundCreate,
    service: PostgresRefundsService = PostgresRefundsService,
) -> SingleRefundResponse:
    refund = await service.create(data)
    return SingleRefundResponse(data=refund)
