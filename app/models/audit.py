from sqlalchemy import Column, String, ForeignKey, DateTime
from datetime import datetime
from app.models.base import BaseModel

class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    user_id = Column(ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

class BlockchainLedger(BaseModel):
    __tablename__ = "blockchain_ledgers"

    case_id = Column(ForeignKey("cases.id"), nullable=False)
    transaction_hash = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
