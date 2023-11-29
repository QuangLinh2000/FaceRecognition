
from sqlalchemy import Column, BLOB, String, ForeignKey
from sqlalchemy.orm import relationship

from src.model.Base import Base


class FaceIdAuth(Base):
    __tablename__ = 'FaceAuth'
    CardNumber = Column(String(250), nullable=True)
    Encoding = Column(BLOB, nullable=False)
    UrlImage = Column(String(250), nullable=False)

