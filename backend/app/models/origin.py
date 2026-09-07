from sqlalchemy import Column, Float, ForeignKey, String
from geoalchemy2 import Geometry

from app.core.database import Base


class SpillOrigin(Base):
    __tablename__ = "spill_origins"

    id = Column(String, primary_key=True, index=True)

    spill_id = Column(
        String,
        ForeignKey("spills.spill_id"),
        nullable=False,
        unique=True
    )

    geometry = Column(
        Geometry(
            geometry_type="POINT",
            srid=4326
        ),
        nullable=False
    )

    uncertainty_km = Column(
        Float,
        nullable=False
    )

    method = Column(
        String,
        nullable=True
    )