from datetime import datetime, timezone
from app import db


store_dive_sites = db.Table(
    "store_dive_sites",
    db.Column("store_id", db.Integer, db.ForeignKey("stores.id"), primary_key=True),
    db.Column("dive_site_id", db.Integer, db.ForeignKey("dive_sites.id"), primary_key=True),
)


class DiveSite(db.Model):
    __tablename__ = "dive_sites"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)

    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    marine_biodiversity = db.Column(db.Float, nullable=False, default=5.0)
    difficulty = db.Column(db.Integer, nullable=False, default=3)
    photography_score = db.Column(db.Float, nullable=False, default=5.0)
    max_depth = db.Column(db.Float, nullable=False, default=20.0)
    marine_life = db.Column(db.String(500), nullable=True)
    crowd_level = db.Column(db.Float, nullable=False, default=0.5)

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    stores = db.relationship("Store", secondary=store_dive_sites, back_populates="dive_sites")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "marine_biodiversity": self.marine_biodiversity,
            "difficulty": self.difficulty,
            "photography_score": self.photography_score,
            "max_depth": self.max_depth,
            "marine_life": [m.strip() for m in self.marine_life.split(",") if m.strip()] if self.marine_life else [],
            "crowd_level": self.crowd_level,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
        }

    def to_recommender_dict(self, weather_data: dict, distance_km: float) -> dict:
        """Build the flat dict that divina_recommender.DiveSite.from_dict() expects."""
        return {
            "id": str(self.id),
            "name": self.name,
            "water_visibility": weather_data.get("water_visibility", 10.0),
            "wave_height": weather_data.get("wave_height", 1.0),
            "current_speed": weather_data.get("current_speed", 0.5),
            "wind_speed": weather_data.get("wind_speed", 10.0),
            "water_temperature": weather_data.get("water_temperature", 20.0),
            "rain_probability": weather_data.get("rain_probability", 0.0),
            "marine_biodiversity": self.marine_biodiversity,
            "difficulty": self.difficulty,
            "photography_score": self.photography_score,
            "max_depth": self.max_depth,
            "marine_life": [m.strip() for m in self.marine_life.split(",") if m.strip()] if self.marine_life else [],
            "distance_km": distance_km,
            "crowd_level": self.crowd_level,
        }

    def __repr__(self):
        return f"<DiveSite {self.name}>"
