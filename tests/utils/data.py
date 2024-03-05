features_data = [
    {
        "id": 100001,
        "name": "First Feature",
        "description": "First Test Feature!",
        "available_entities": [],
    },
    {
        "id": 100002,
        "name": "Second Feature",
        "description": "Second Test Feature!",
        "available_entities": [],
    },
    {
        "id": 100003,
        "name": "Third Feature",
        "description": "Third Test Feature!",
        "available_entities": [],
    },
]

plans_data = [
    {
        "id": 100001,
        "name": "First Plan",
        "description": "",
        "is_active": True,
        "is_recurring": True,
        "duration": "1",
        "duration_unit": "month",
    },
    {
        "id": 100002,
        "name": "Second Plan",
        "description": "",
        "is_active": False,
        "is_recurring": True,
        "duration": "1",
        "duration_unit": "month",
    },
    {
        "id": 100003,
        "name": "Third Plan",
        "description": "",
        "is_active": True,
        "is_recurring": False,
        "duration": "1",
        "duration_unit": "month",
    },
]

payments_data = [
    {
        "id": 1000001,
        "payment_provider_id": 1000001,
        "payment_method": "bank_card",
        "status": "created",
        "currency": "RUB",
        "amount": 100.00,
        "external_payment_id": None,
        "external_payment_type_id": None,
    },
    {
        "id": 1000002,
        "payment_provider_id": 1000001,
        "payment_method": "bank_card",
        "status": "succeeded",
        "currency": "RUB",
        "amount": 300.00,
        "external_payment_id": None,
        "external_payment_type_id": None,
    },
    {
        "id": 1000003,
        "payment_provider_id": 1000001,
        "payment_method": "bank_card",
        "status": "cancelled",
        "currency": "RUB",
        "amount": 300.00,
        "external_payment_id": None,
        "external_payment_type_id": None,
    },
]

prices_data = [
    {"id": 1000001, "plan_id": 1000001, "currency": "RUB", "amount": 100.00},
    {"id": 1000002, "plan_id": 1000002, "currency": "RUB", "amount": 200.00},
    {"id": 1000003, "plan_id": 1000003, "currency": "RUB", "amount": 300.00},
]


subscriptions_data = [
    {
        "id": 1000001,
        "plan_id": 1000001,
        "payment_provider_id": 1000001,
        "currency": "RUB",
        "payment_method": "bank_card",
        "user_id": "cc6e0b24-a46f-4c8e-beb0-b28479f3b203",
        "return_url": None,
    },
    {
        "id": 1000002,
        "plan_id": 1000001,
        "payment_provider_id": 1000001,
        "currency": "RUB",
        "payment_method": "bank_card",
        "user_id": "c849081f-9a99-4ff0-aa54-33118d2abaee",
        "return_url": None,
    },
    {
        "id": 1000003,
        "plan_id": 1000001,
        "payment_provider_id": 1000001,
        "currency": "RUB",
        "payment_method": "bank_card",
        "user_id": "c849081f-9a99-4ff0-aa54-33118d2abaee",
        "return_url": None,
    },
]

payment_providers = [{"id": 1000001, "name": "Yookassa", "description": None, "is_active": True}]

