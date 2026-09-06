from sqlalchemy import Column, Float, ForeignKey, String

from app.core.database import Base


class VesselAttribution(Base):
    __tablename__ = "vessel_attributions"

    id = Column(String, primary_key=True, index=True)

    spill_id = Column(
        String,
        ForeignKey("spills.spill_id"),
        nullable=False
    )

    mmsi = Column(
        String,
        ForeignKey("vessels.mmsi"),
        nullable=False
    )

    attribution_score = Column(
        Float,
        nullable=False
    )

    distance_km = Column(
        Float,
        nullable=True
    )

    time_difference_hours = Column(
        Float,
        nullable=True
    )

    trajectory_match_score = Column(
        Float,
        nullable=True
    )

    behavioral_anomaly_score = Column(
        Float,
        nullable=True
    )