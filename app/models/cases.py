from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Case(BaseModel):
    __tablename__ = "cases"

    citizen_id = Column(ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, default="pending", nullable=False)
    priority = Column(Integer, default=0)
    citizen_notification_preference = Column(String, default="email")
    
    # Geolocation
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    ward = Column(String, nullable=True)
    
    # AI Processed Data
    ai_severity = Column(Integer, nullable=True)
    ai_intent = Column(String, nullable=True)
    assigned_department = Column(String, nullable=True)
    
    closed_at = Column(DateTime, nullable=True)

    attachments = relationship("MediaAttachment", back_populates="case_record")


class MediaAttachment(BaseModel):
    __tablename__ = "media_attachments"

    case_id = Column(ForeignKey("cases.id"), nullable=False)
    file_url = Column(String, nullable=False)
    media_type = Column(String, nullable=False) # e.g., image, video
    stage = Column(String, nullable=False) # e.g., before, after
    
    case_record = relationship("Case", back_populates="attachments")
