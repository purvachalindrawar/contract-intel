
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from .db import Base
import datetime

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
    metadata_json = Column("metadata", JSON, default={})
    full_text = Column(Text, default="")
    pages = Column(JSON, default=[])
