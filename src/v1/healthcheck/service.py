from src.v1.healthcheck.models import HealthCheck


class HealthCheckService:
    @staticmethod
    async def get_status() -> HealthCheck:
        response = {
            "status": "OK",
            "message": "Service is available right now.",
        }
        return HealthCheck(**response)
