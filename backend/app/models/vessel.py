from sqlalchemy import Column, Float, String

from app.core.database import Base


class Vessel(Base):
    __tablename__ = "vessels"

    mmsi = Column(String, primary_key=True, index=True)
    vessel_name = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    speed_knots = Column(Float, nullable=True)
    course = Column(Float, nullable=True)
