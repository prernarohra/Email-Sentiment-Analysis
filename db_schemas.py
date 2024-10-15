from sqlalchemy import Boolean, Column, Integer, String, DateTime

from database import Base

class EmailSentiments(Base):
    __tablename__ = "Email-Sentiments"

    id = Column(Integer, primary_key=True)
    content = Column(String)
    sentiment = Column(String)
    created_date = Column(DateTime)
    is_deleted = Column(Boolean, default=True)
