from sqlalchemy import Column, Float, ForeignKey, Integer, String

from app.core.database import Base


class DriftPoint(Base):
    __tablename__ = "drift_points"

    id = Column(Integer, primary_key=True, autoincrement=True)

    spill_id = Column(
        String,
        ForeignKey("spills.spill_id"),
        nullable=False
    )

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    hours_from_detection = Column(Float, nullable=False)

    current_speed = Column(Float, nullable=True)
    current_direction = Column(Float, nullable=True)

    wind_speed = Column(Float, nullable=True)
    wind_direction = Column(Float, nullable=True)