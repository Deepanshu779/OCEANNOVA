from sqlalchemy import Column, Float, String, DateTime
from geoalchemy2 import Geometry

from app.core.database import Base


class Spill(Base):
    __tablename__ = "spills"

    spill_id = Column(String, primary_key=True, index=True)
    confidence = Column(Float, nullable=False)
    area_km2 = Column(Float, nullable=False)
    acquisition_time = Column(DateTime, nullable=True)
    perimeter_km = Column(Float, nullable=True)
    compactness = Column(Float, nullable=True)
    estimated_age_hours = Column(Float, nullable=True)
    geometry = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
