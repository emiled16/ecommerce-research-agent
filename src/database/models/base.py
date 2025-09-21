from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func
from src.database.database import Base


class BaseModel(Base):
    __abstract__ = True

    created_at = Column(DateTime, server_default=func.now())

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
