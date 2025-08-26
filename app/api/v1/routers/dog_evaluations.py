from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import math

from app.core.deps import get_db, get_current_active_user
from app.models.user import User, UserRole
from app.models.dog import Dog
from app.models.owner import Owner
from app.models.dog_evaluation import DogEvaluation
from app.schemas.dog_evaluation import (
    DogEvaluationCreate, 
    DogEvaluationUpdate, 
    DogEvaluationOut, 
    DogEvaluationListResponse,
    DogEvaluationSummary
)

router = APIRouter()


def _can_create_evaluation(current_user: User) -> bool:
    """評価作成権限チェック"""
    return current_user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]


def _can_view_evaluation(db: Session, current_user: User, dog_id: str) -> bool:
    """評価閲覧権限チェック（管理者 + 犬の飼い主）"""
    if current_user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        return True
    
    # 犬の飼い主かチェック
    if current_user.owner:
        dog = db.query(Dog).filter(Dog.id == dog_id).first()
        if dog and dog.owner_id == current_user.owner.id:
            return True
    
    return False


def _can_update_evaluation(current_user: User, evaluation: DogEvaluation) -> bool:
    """評価更新権限チェック（管理者 + 評価者本人）"""
    if current_user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        return True
    
    # 評価者本人かチェック
    if evaluation.evaluator_user_id == current_user.id:
        return True
    
    return False


@router.post("/", response_model=DogEvaluationOut)
def create_dog_evaluation(
    evaluation_create: DogEvaluationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # 権限チェック
    if not _can_create_evaluation(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="評価を作成する権限がありません"
        )
    
    # 犬の存在チェック
    dog = db.query(Dog).filter(Dog.id == evaluation_create.dog_id).first()
    if not dog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指定された犬が見つかりません"
        )
    
    # 評価作成
    db_evaluation = DogEvaluation(
        dog_id=evaluation_create.dog_id,
        evaluated_on=evaluation_create.evaluated_on,
        ears=evaluation_create.ears,
        muzzle=evaluation_create.muzzle,
        neck=evaluation_create.neck,
        back=evaluation_create.back,
        paws=evaluation_create.paws,
        tail=evaluation_create.tail,
        human_affinity_score=evaluation_create.human_affinity_score,
        dog_affinity_score=evaluation_create.dog_affinity_score,
        noise_tolerance_score=evaluation_create.noise_tolerance_score,
        crate_tolerance_score=evaluation_create.crate_tolerance_score,
        concerns=evaluation_create.concerns,
        strengths=evaluation_create.strengths,
        evaluator_user_id=current_user.id
    )
    
    db.add(db_evaluation)
    db.commit()
    db.refresh(db_evaluation)
    
    return db_evaluation


@router.get("/", response_model=DogEvaluationListResponse)
def list_dog_evaluations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    dog_id: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    query = db.query(DogEvaluation)
    
    # 一般ユーザーは自分の犬のみ
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        if not current_user.owner:
            return DogEvaluationListResponse(items=[], total=0, page=page, size=size, pages=0)
        
        # 飼い犬IDを取得
        owned_dog_ids = [dog.id for dog in current_user.owner.dogs]
        if not owned_dog_ids:
            return DogEvaluationListResponse(items=[], total=0, page=page, size=size, pages=0)
        
        query = query.filter(DogEvaluation.dog_id.in_(owned_dog_ids))
    
    # フィルタ適用
    if dog_id:
        query = query.filter(DogEvaluation.dog_id == dog_id)
    
    if date_from:
        query = query.filter(DogEvaluation.evaluated_on >= date_from)
    
    if date_to:
        query = query.filter(DogEvaluation.evaluated_on <= date_to)
    
    # 評価日降順でソート
    query = query.order_by(DogEvaluation.evaluated_on.desc())
    
    # 件数取得
    total = query.count()
    
    # ページネーション適用
    offset = (page - 1) * size
    evaluations = query.offset(offset).limit(size).all()
    
    # ページ数計算
    pages = math.ceil(total / size) if total > 0 else 0
    
    return DogEvaluationListResponse(
        items=evaluations,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{evaluation_id}", response_model=DogEvaluationOut)
def get_dog_evaluation(
    evaluation_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    evaluation = db.query(DogEvaluation).filter(DogEvaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="評価が見つかりません"
        )
    
    # 閲覧権限チェック
    if not _can_view_evaluation(db, current_user, evaluation.dog_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="この評価を閲覧する権限がありません"
        )
    
    return evaluation


@router.patch("/{evaluation_id}", response_model=DogEvaluationOut)
def update_dog_evaluation(
    evaluation_id: str,
    evaluation_update: DogEvaluationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    evaluation = db.query(DogEvaluation).filter(DogEvaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="評価が見つかりません"
        )
    
    # 更新権限チェック
    if not _can_update_evaluation(current_user, evaluation):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="この評価を更新する権限がありません"
        )
    
    # 更新データ適用
    update_data = evaluation_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(evaluation, field, value)
    
    db.commit()
    db.refresh(evaluation)
    
    return evaluation


@router.delete("/{evaluation_id}")
def delete_dog_evaluation(
    evaluation_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    evaluation = db.query(DogEvaluation).filter(DogEvaluation.id == evaluation_id).first()
    if not evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="評価が見つかりません"
        )
    
    # 削除権限チェック（管理者のみ）
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="評価を削除する権限がありません"
        )
    
    db.delete(evaluation)
    db.commit()
    
    return {"detail": "評価が正常に削除されました"}


@router.get("/dogs/{dog_id}/evaluations", response_model=DogEvaluationListResponse)
def get_dog_evaluations(
    dog_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    # 犬の存在チェック
    dog = db.query(Dog).filter(Dog.id == dog_id).first()
    if not dog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指定された犬が見つかりません"
        )
    
    # 閲覧権限チェック
    if not _can_view_evaluation(db, current_user, dog_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="この犬の評価を閲覧する権限がありません"
        )
    
    query = db.query(DogEvaluation).filter(DogEvaluation.dog_id == dog_id)
    query = query.order_by(DogEvaluation.evaluated_on.desc())
    
    # 件数取得
    total = query.count()
    
    # ページネーション適用
    offset = (page - 1) * size
    evaluations = query.offset(offset).limit(size).all()
    
    # ページ数計算
    pages = math.ceil(total / size) if total > 0 else 0
    
    return DogEvaluationListResponse(
        items=evaluations,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/dogs/{dog_id}/latest-evaluation", response_model=DogEvaluationOut)
def get_latest_dog_evaluation(
    dog_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # 犬の存在チェック
    dog = db.query(Dog).filter(Dog.id == dog_id).first()
    if not dog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="指定された犬が見つかりません"
        )
    
    # 閲覧権限チェック
    if not _can_view_evaluation(db, current_user, dog_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="この犬の評価を閲覧する権限がありません"
        )
    
    # 最新評価を取得
    latest_evaluation = (
        db.query(DogEvaluation)
        .filter(DogEvaluation.dog_id == dog_id)
        .order_by(DogEvaluation.evaluated_on.desc())
        .first()
    )
    
    if not latest_evaluation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="この犬の評価が見つかりません"
        )
    
    return latest_evaluation