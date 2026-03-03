from datetime import datetime, timezone
from app import db
from divina_recommender.models import UserPreferences as RecUserPreferences


class UserDivePreferences(db.Model):
    __tablename__ = "user_dive_preferences"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    skill_level = db.Column(db.Integer, nullable=False, default=3)
    preferred_marine_life = db.Column(db.String(500), nullable=True)
    photography_priority = db.Column(db.Float, nullable=False, default=5.0)
    depth_preference = db.Column(db.Float, nullable=False, default=20.0)
    max_travel_distance = db.Column(db.Float, nullable=False, default=50.0)
    requires_rental = db.Column(db.Boolean, default=False)
    requires_nitrox = db.Column(db.Boolean, default=False)
    requires_training = db.Column(db.Boolean, default=False)
    is_tech_diver = db.Column(db.Boolean, default=False)
    preferred_price_level = db.Column(db.Integer, nullable=True)

    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = db.relationship("User", backref=db.backref("dive_preferences", uselist=False, lazy=True))

    def to_dict(self) -> dict:
        return {
            "skill_level": self.skill_level,
            "preferred_marine_life": [m.strip() for m in self.preferred_marine_life.split(",") if m.strip()] if self.preferred_marine_life else [],
            "photography_priority": self.photography_priority,
            "depth_preference": self.depth_preference,
            "max_travel_distance": self.max_travel_distance,
            "requires_rental": self.requires_rental,
            "requires_nitrox": self.requires_nitrox,
            "requires_training": self.requires_training,
            "is_tech_diver": self.is_tech_diver,
            "preferred_price_level": self.preferred_price_level,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_recommender_obj(self) -> RecUserPreferences:
        """Convert to the recommender engine's UserPreferences dataclass."""
        return RecUserPreferences(
            skill_level=self.skill_level,
            preferred_marine_life=[m.strip() for m in self.preferred_marine_life.split(",") if m.strip()] if self.preferred_marine_life else [],
            photography_priority=self.photography_priority,
            depth_preference=self.depth_preference,
            max_travel_distance=self.max_travel_distance,
            requires_rental=self.requires_rental,
            requires_nitrox=self.requires_nitrox,
            requires_training=self.requires_training,
            is_tech_diver=self.is_tech_diver,
            preferred_price_level=self.preferred_price_level,
        )

    def __repr__(self):
        return f"<UserDivePreferences user_id={self.user_id}>"
