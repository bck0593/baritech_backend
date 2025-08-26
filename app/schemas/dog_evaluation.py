from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Optional, List

from app.models.dog_evaluation import BodyPartAssessment


class DogEvaluationCreate(BaseModel):
    dog_id: str
    evaluated_on: date
    
    # 身体各部位の評価（オプショナル）
    ears: Optional[BodyPartAssessment] = None
    muzzle: Optional[BodyPartAssessment] = None
    neck: Optional[BodyPartAssessment] = None
    back: Optional[BodyPartAssessment] = None
    paws: Optional[BodyPartAssessment] = None
    tail: Optional[BodyPartAssessment] = None
    
    # スコア評価（1-10点、オプショナル）
    human_affinity_score: Optional[int] = None
    dog_affinity_score: Optional[int] = None
    noise_tolerance_score: Optional[int] = None
    crate_tolerance_score: Optional[int] = None
    
    # 評価詳細
    concerns: Optional[str] = None
    strengths: Optional[str] = None

    @field_validator('human_affinity_score', 'dog_affinity_score', 'noise_tolerance_score', 'crate_tolerance_score')
    @classmethod
    def validate_scores(cls, v):
        if v is not None and (v < 1 or v > 10):
            raise ValueError('スコアは1から10の間で入力してください')
        return v


class DogEvaluationUpdate(BaseModel):
    evaluated_on: Optional[date] = None
    
    # 身体各部位の評価
    ears: Optional[BodyPartAssessment] = None
    muzzle: Optional[BodyPartAssessment] = None
    neck: Optional[BodyPartAssessment] = None
    back: Optional[BodyPartAssessment] = None
    paws: Optional[BodyPartAssessment] = None
    tail: Optional[BodyPartAssessment] = None
    
    # スコア評価
    human_affinity_score: Optional[int] = None
    dog_affinity_score: Optional[int] = None
    noise_tolerance_score: Optional[int] = None
    crate_tolerance_score: Optional[int] = None
    
    # 評価詳細
    concerns: Optional[str] = None
    strengths: Optional[str] = None

    @field_validator('human_affinity_score', 'dog_affinity_score', 'noise_tolerance_score', 'crate_tolerance_score')
    @classmethod
    def validate_scores(cls, v):
        if v is not None and (v < 1 or v > 10):
            raise ValueError('スコアは1から10の間で入力してください')
        return v


class DogEvaluationOut(BaseModel):
    id: str
    dog_id: str
    evaluated_on: date
    
    # 身体各部位の評価
    ears: Optional[BodyPartAssessment] = None
    muzzle: Optional[BodyPartAssessment] = None
    neck: Optional[BodyPartAssessment] = None
    back: Optional[BodyPartAssessment] = None
    paws: Optional[BodyPartAssessment] = None
    tail: Optional[BodyPartAssessment] = None
    
    # スコア評価
    human_affinity_score: Optional[int] = None
    dog_affinity_score: Optional[int] = None
    noise_tolerance_score: Optional[int] = None
    crate_tolerance_score: Optional[int] = None
    
    # 評価詳細
    concerns: Optional[str] = None
    strengths: Optional[str] = None
    evaluator_user_id: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DogEvaluationListResponse(BaseModel):
    items: List[DogEvaluationOut]
    total: int
    page: int
    size: int
    pages: int


class DogEvaluationSummary(BaseModel):
    """犬の評価サマリー（最新評価の概要）"""
    id: str
    evaluated_on: date
    overall_score: Optional[float] = None  # 全スコアの平均
    has_concerns: bool = False  # 懸念点があるかどうか
    evaluator_user_id: Optional[str] = None

    model_config = {"from_attributes": True}