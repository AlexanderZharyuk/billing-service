from sqlmodel import SQLModel


class HealthCheck(SQLModel):
    status: str
    message: str
