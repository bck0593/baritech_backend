from sqlalchemy import Column, String, Enum, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
import enum

from app.db.session import Base


class UserStatus(enum.Enum):
    ACTIVE = "有効"
    INACTIVE = "無効"
    SUSPENDED = "停止"


class UserRole(enum.Enum):
    USER = "利用者"
    ADMIN = "管理者"
    SUPER_ADMIN = "スーパー管理者"


class User(Base):
    __tablename__ = "ユーザー"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    status = Column(Enum(UserStatus, values_callable=lambda obj: [e.value for e in obj]), default=UserStatus.ACTIVE, nullable=False)
    role = Column(Enum(UserRole, values_callable=lambda obj: [e.value for e in obj]), default=UserRole.USER, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships - Phase 4C: User-Like relationship enabled
    owner = relationship("Owner", back_populates="user", uselist=False)
    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    likes = relationship("Like", back_populates="user")
    # notifications = relationship("Notification", back_populates="user") - Phase 8