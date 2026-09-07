from sqlalchemy import Column, Float, ForeignKey, Integer, String

from app.core.database import Base


class VesselTrackPoint(Base):
    __tablename__ = "vessel_track_points"

    id = Column(Integer, primary_key=True, autoincrement=True)
    mmsi = Column(String, ForeignKey("vessels.mmsi"), nullable=False, index=True)
    timestamp_hours_from_origin = Column(Float, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    speed_knots = Column(Float, nullable=True)
    course = Column(Float, nullable=True)
