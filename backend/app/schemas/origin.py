from pydantic import BaseModel


class OriginResponse(BaseModel):
    latitude: float
    longitude: float
    uncertainty_km: float
    method: str | None = None