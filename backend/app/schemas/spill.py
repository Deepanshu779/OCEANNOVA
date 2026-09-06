from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    lat: float = Field(
        ...,
        ge=-90,
        le=90,
        description="Latitude in WGS84"
    )

    lon: float = Field(
        ...,
        ge=-180,
        le=180,
        description="Longitude in WGS84"
    )


class GeoJSONPoint(BaseModel):
    type: Literal["Point"] = "Point"

    coordinates: list[float] = Field(
        ...,
        min_length=2,
        max_length=2,
        description="[longitude, latitude]"
    )


class SpillCreate(BaseModel):
    spill_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique spill identifier"
    )

    confidence: float = Field(
        ...,
        ge=0,
        le=1,
        description="Detection confidence between 0 and 1"
    )

    area_km2: float = Field(
        ...,
        ge=0,
        description="Estimated spill area in square kilometers"
    )

    centroid: Coordinates

    acquisition_time: Optional[datetime] = None


class SpillResponse(SpillCreate):
    status: str = "detected"
    geometry: GeoJSONPoint