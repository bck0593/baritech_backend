from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_active_user, get_current_admin_user
from app.core.pagination import PaginatedResponse
from app.models.user import User
from app.schemas.health_record import HealthRecordCreate, HealthRecordUpdate, HealthRecordOut
from app.services.health_record_service import get_health_record_service, HealthRecordService

router = APIRouter()


@router.post("/", response_model=HealthRecordOut, status_code=status.HTTP_201_CREATED)
def create_health_record(
    record_data: HealthRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # 管理者のみ作成可能
):
    """健康記録を作成"""
    record_service = get_health_record_service(db)
    return record_service.create_health_record(record_data)


@router.get("/", response_model=PaginatedResponse[HealthRecordOut])
def list_health_records(
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(10, ge=1, le=100, description="1ページあたりの件数"),
    dog_id: Optional[str] = Query(None, description="犬ID"),
    record_date_from: Optional[date] = Query(None, description="記録日（開始）"),
    record_date_to: Optional[date] = Query(None, description="記録日（終了）"),
    weight_min: Optional[float] = Query(None, description="最小体重(kg)"),
    weight_max: Optional[float] = Query(None, description="最大体重(kg)"),
    temperature_min: Optional[float] = Query(None, description="最低体温(℃)"),
    temperature_max: Optional[float] = Query(None, description="最高体温(℃)"),
    sort_by: str = Query("record_date", description="ソートフィールド"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="ソート順序"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """健康記録一覧を取得（フィルタ・ページネーション対応）"""
    record_service = get_health_record_service(db)
    
    return record_service.get_health_records(
        page=page,
        page_size=page_size,
        dog_id=dog_id,
        record_date_from=record_date_from,
        record_date_to=record_date_to,
        weight_min=weight_min,
        weight_max=weight_max,
        temperature_min=temperature_min,
        temperature_max=temperature_max,
        sort_by=sort_by,
        sort_order=sort_order
    )


@router.get("/{record_id}", response_model=HealthRecordOut)
def get_health_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """健康記録を ID で取得"""
    record_service = get_health_record_service(db)
    record = record_service.get_health_record(record_id)
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health record not found"
        )
    
    return record


@router.put("/{record_id}", response_model=HealthRecordOut)
def update_health_record(
    record_id: str,
    record_data: HealthRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # 管理者のみ更新可能
):
    """健康記録を更新"""
    record_service = get_health_record_service(db)
    record = record_service.update_health_record(record_id, record_data)
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health record not found"
        )
    
    return record


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_health_record(
    record_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # 管理者のみ削除可能
):
    """健康記録を削除"""
    record_service = get_health_record_service(db)
    success = record_service.delete_health_record(record_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Health record not found"
        )


@router.get("/by-dog/{dog_id}", response_model=list[HealthRecordOut])
def get_health_records_by_dog(
    dog_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """特定の犬の健康記録をすべて取得"""
    record_service = get_health_record_service(db)
    return record_service.get_health_records_by_dog(dog_id)


@router.get("/recent/", response_model=PaginatedResponse[HealthRecordOut])
def get_recent_health_records(
    days: int = Query(30, ge=1, description="過去何日分の記録を取得するか"),
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(10, ge=1, le=100, description="1ページあたりの件数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """最近の健康記録を取得"""
    record_service = get_health_record_service(db)
    return record_service.get_recent_health_records(days, page, page_size)


@router.get("/search/", response_model=PaginatedResponse[HealthRecordOut])
def search_health_records(
    q: str = Query(..., min_length=1, description="検索キーワード"),
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(10, ge=1, le=100, description="1ページあたりの件数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """健康記録を検索"""
    record_service = get_health_record_service(db)
    return record_service.search_health_records(q, page, page_size)