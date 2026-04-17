from datetime import datetime, timezone
from uuid import uuid7

from src.app.database import Base
from sqlalchemy import Column, String, Enum, Float, Integer, DateTime, event


class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True, index=True,
                default=lambda: str(uuid7()))
    name = Column(String, nullable=False, unique=True)
    gender = Column(Enum('male', 'female', name='gender_enum'), nullable=False, default='male')
    gender_probability = Column(Float, nullable=False)
    sample_size = Column(Integer, nullable=False)
    age = Column(Integer, nullable=False)
    age_group = Column(String, nullable=False)
    country_id = Column(String, nullable=False)
    country_probability = Column(Float, nullable=False)
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime
        .now(timezone.utc)
        .replace(microsecond=0)
    )


@event.listens_for(User, 'before_insert')
def set_age_group(mapper, connection, target):
    if target.age <= 12:
        target.age_group = "child"
    elif target.age <= 19:
        target.age_group = "teenager"
    elif target.age < 60:
        target.age_group = "adult"
    else:
        target.age_group = "senior"
