from sqlalchemy import Column, String, Date, Integer, Enum, Text, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4
import enum

from app.db.session import Base


class BodyPartAssessment(enum.Enum):
    OK = "OK"
    SLIGHTLY_DISLIKES = "少し嫌がる"
    CLEARLY_DISLIKES = "明確に嫌がる"


class DogEvaluation(Base):
    __tablename__ = "犬評価"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    dog_id = Column(String, ForeignKey("犬.id"), nullable=False)
    evaluated_on = Column(Date, nullable=False)
    
    # 身体各部位の評価
    ears = Column(Enum(BodyPartAssessment, values_callable=lambda obj: [e.value for e in obj]), nullable=True)
    muzzle = Column(Enum(BodyPartAssessment, values_callable=lambda obj: [e.value for e in obj]), nullable=True)
    neck = Column(Enum(BodyPartAssessment, values_callable=lambda obj: [e.value for e in obj]), nullable=True)
    back = Column(Enum(BodyPartAssessment, values_callable=lambda obj: [e.value for e in obj]), nullable=True)
    paws = Column(Enum(BodyPartAssessment, values_callable=lambda obj: [e.value for e in obj]), nullable=True)
    tail = Column(Enum(BodyPartAssessment, values_callable=lambda obj: [e.value for e in obj]), nullable=True)
    
    # スコア評価（1-10点）
    human_affinity_score = Column(Integer, nullable=True)  # 人なれスコア
    dog_affinity_score = Column(Integer, nullable=True)    # 犬なれスコア
    noise_tolerance_score = Column(Integer, nullable=True) # 物音耐性スコア
    crate_tolerance_score = Column(Integer, nullable=True) # クレート耐性スコア
    
    # 評価詳細
    concerns = Column(Text, nullable=True)    # 懸念点
    strengths = Column(Text, nullable=True)   # 強み
    evaluator_user_id = Column(String, ForeignKey("ユーザー.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    # Note: updated_at column doesn't exist in Azure MySQL table

    # Relationships - Phase 3: DogEvaluation relationships enabled
    dog = relationship("Dog", back_populates="evaluations")
    # evaluator = relationship("User", back_populates="dog_evaluations") - Phase 5

    # Indexes
    __table_args__ = (
        Index('ix_dog_evaluations_dog_id', 'dog_id'),
        Index('ix_dog_evaluations_evaluated_on', 'evaluated_on'),
        Index('ix_dog_evaluations_evaluator_user_id', 'evaluator_user_id'),
    )