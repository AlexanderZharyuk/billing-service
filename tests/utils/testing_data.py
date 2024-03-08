from datetime import datetime
from src.v1.payments.models import PaymentStatusEnum, PaymentMethodsEnum
from src.v1.subscriptions.models import SubscriptionStatusEnum, CurrencyEnum
from src.v1.refunds.models import RefundTicketStatusEnum

test_data = {
    "features": [
        {
            "name": "First Feature",
            "description": "First Test Feature!",
            "available_entities": ["Sport"],
            "created_at": datetime(2024, 1, 1),
            "updated_at": datetime(2024, 1, 1),
        },
        {
            "name": "Second Feature",
            "description": "Second Test Feature!",
            "available_entities": ['Premier'],
            "created_at": datetime(2024, 1, 1),
            "updated_at": datetime(2024, 1, 1),
        },
        {
            "name": "Third Feature",
            "description": "Third Test Feature!",
            "available_entities": ["18+"],
            "created_at": datetime(2024, 1, 1),
            "updated_at": datetime(2024, 1, 1),
        },
    ],
    "plans": [
        {
            "name": "First Plan",
            "description": "",
            "is_active": True,
            "is_recurring": True,
            "duration": 1,
            "duration_unit": "month",
            "created_at": datetime(2024, 1, 1),
            "updated_at": datetime(2024, 1, 1),
        },
        {
            "name": "Second Plan",
            "description": "",
            "is_active": False,
            "is_recurring": True,
            "duration": 1,
            "duration_unit": "month",
            "created_at": datetime(2024, 1, 1),
            "updated_at": datetime(2024, 1, 1),
        },
        {
            "name": "Third Plan",
            "description": "",
            "is_active": True,
            "is_recurring": False,
            "duration": 1,
            "duration_unit": "month",
            "created_at": datetime(2024, 1, 1),
            "updated_at": datetime(2024, 1, 1),
        },
    ],
    "payments": [
        {
            "payment_provider_id": 1,
            "payment_method": PaymentMethodsEnum.BANK_CARD,
            "status": PaymentStatusEnum.CREATED,
            "subscription_id": 1,
            "currency": "RUB",
            "amount": 100.00,
            "external_payment_id": None,
            "external_payment_type_id": None,
            "created_at": datetime(2024, 1, 1),
            "updated_at": datetime(2024, 1, 1),
        },
        {
            "payment_provider_id": 1,
            "payment_method": PaymentMethodsEnum.BANK_CARD,
            "status": PaymentStatusEnum.SUCCEEDED,
            "subscription_id": 2,
            "currency": "RUB",
            "amount": 200.00,
            "external_payment_id": None,
            "external_payment_type_id": None,
            "created_at": datetime(2024, 1, 1),
            "updated_at": datetime(2024, 1, 1),
        },
        {
            "payment_provider_id": 1,
            "payment_method": PaymentMethodsEnum.BANK_CARD,
            "status": PaymentStatusEnum.CANCELED,
            "subscription_id": 3,
            "currency": CurrencyEnum.RUB,
            "amount": 300.00,
            "external_payment_id": None,
            "external_payment_type_id": None,
            "created_at": datetime(2024, 1, 1),
            "updated_at": datetime(2024, 1, 1),
        },
    ],
    "prices": [
        {
            "plan_id": 1,
            "currency": CurrencyEnum.RUB,
            "amount": 100.00,
            "created_at": datetime(2024, 1, 1),
            "updated_at": datetime(2024, 1, 1),
        },
        {
            "plan_id": 2,
            "currency": CurrencyEnum.RUB,
            "amount": 200.00,
            "created_at": datetime(2024, 1, 1),
            "updated_at": datetime(2024, 1, 1),
        },
    ],
    "subscriptions": [
        {
            "plan_id": 1,
            "user_id": "3f8cd1fb-0cc0-4e99-ba39-9478fa007731",
            "status": SubscriptionStatusEnum.ACTIVE,
            "started_at": datetime(2024, 1, 1),
            "ended_at": datetime(2024, 1, 31),
            "created_at": datetime(2024, 1, 1),
            "updated_at": datetime(2024, 1, 1),
        },
        {
            "plan_id": 1,
            "user_id": "cc6e0b24-a46f-4c8e-beb0-b28479f3b202",
            "status": SubscriptionStatusEnum.CREATED,
            "started_at": datetime(2024, 1, 1),
            "ended_at": datetime(2024, 1, 31),
            "created_at": datetime(2024, 1, 1),
            "updated_at": datetime(2024, 1, 1),
        },
        {
            "plan_id": 1,
            "user_id": "cc6e0b24-a46f-4c8e-beb0-b28479f3b203",
            "status": SubscriptionStatusEnum.ACTIVE,
            "started_at": datetime(2024, 1, 1),
            "ended_at": datetime(2024, 1, 31),
            "created_at": datetime(2024, 1, 1),
            "updated_at": datetime(2024, 1, 1),
        },
    ],
    "payment_providers": [
        {"name": "Yookassa", "description": None, "is_active": True}
    ],
    "refund_reasons": [
        {"name": "Other"}
    ],
    "refunds": [
        {"reason_id": 1,
         "subscription_id": 1,
         "user_id": "3f8cd1fb-0cc0-4e99-ba39-9478fa007731",
         "additional_info": "No comment",
         "status": RefundTicketStatusEnum.OPEN
         }
    ],
}
