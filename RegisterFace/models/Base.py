from datetime import datetime
import uuid

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String,Boolean,DATETIME


class Base(DeclarativeBase):
    ID = Column(String(250), nullable=False, primary_key=True, unique=True, default= str(uuid.uuid4().hex))
    IsDelete = Column(Boolean, default=False)
    IsInsert = Column(Boolean, default=False)
    IsUpdate = Column(Boolean, default=False)
    CreatedAt = Column(DATETIME, nullable=False,default=datetime.utcnow())
    UpdatedAt = Column(DATETIME, nullable=False,default=datetime.utcnow())

