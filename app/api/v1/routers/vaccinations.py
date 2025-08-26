from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_active_user, get_current_admin_user
from app.core.pagination import PaginatedResponse
from app.models.user import User
from app.schemas.vaccination import VaccinationCreate, VaccinationUpdate, VaccinationOut
from app.services.vaccination_service import get_vaccination_service, VaccinationService

router = APIRouter()


@router.post("/", response_model=VaccinationOut, status_code=status.HTTP_201_CREATED)
def create_vaccination(
    vaccination_data: VaccinationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # 管理者のみ作成可能
):
    """予防接種記録を作成"""
    vaccination_service = get_vaccination_service(db)
    return vaccination_service.create_vaccination(vaccination_data)


@router.get("/{vaccination_id}", response_model=VaccinationOut)
def get_vaccination(
    vaccination_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """予防接種記録を ID で取得"""
    vaccination_service = get_vaccination_service(db)
    vaccination = vaccination_service.get_vaccination(vaccination_id)
    
    if not vaccination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vaccination record not found"
        )
    
    return vaccination


@router.get("/", response_model=PaginatedResponse[VaccinationOut])
def list_vaccinations(
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(10, ge=1, le=100, description="1ページあたりの件数"),
    dog_id: Optional[str] = Query(None, description="犬ID"),
    vaccine_name: Optional[str] = Query(None, description="ワクチン名（部分一致）"),
    administered_from: Optional[date] = Query(None, description="接種日（開始）"),
    administered_to: Optional[date] = Query(None, description="接種日（終了）"),
    due_from: Optional[date] = Query(None, description="次回接種予定日（開始）"),
    due_to: Optional[date] = Query(None, description="次回接種予定日（終了）"),
    sort_by: str = Query("administered_on", description="ソートフィールド"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="ソート順序"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """予防接種記録一覧を取得（フィルタ・ページネーション対応）"""
    vaccination_service = get_vaccination_service(db)
    
    return vaccination_service.get_vaccinations(
        page=page,
        page_size=page_size,
        dog_id=dog_id,
        vaccine_name=vaccine_name,
        administered_from=administered_from,
        administered_to=administered_to,
        due_from=due_from,
        due_to=due_to,
        sort_by=sort_by,
        sort_order=sort_order
    )


@router.put("/{vaccination_id}", response_model=VaccinationOut)
def update_vaccination(
    vaccination_id: str,
    vaccination_data: VaccinationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # 管理者のみ更新可能
):
    """予防接種記録を更新"""
    vaccination_service = get_vaccination_service(db)
    vaccination = vaccination_service.update_vaccination(vaccination_id, vaccination_data)
    
    if not vaccination:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vaccination record not found"
        )
    
    return vaccination


@router.delete("/{vaccination_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vaccination(
    vaccination_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # 管理者のみ削除可能
):
    """予防接種記録を削除"""
    vaccination_service = get_vaccination_service(db)
    success = vaccination_service.delete_vaccination(vaccination_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vaccination record not found"
        )


@router.get("/by-dog/{dog_id}", response_model=list[VaccinationOut])
def get_vaccinations_by_dog(
    dog_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """特定の犬の予防接種記録をすべて取得"""
    vaccination_service = get_vaccination_service(db)
    return vaccination_service.get_vaccinations_by_dog(dog_id)


@router.get("/upcoming/", response_model=PaginatedResponse[VaccinationOut])
def get_upcoming_vaccinations(
    days_ahead: int = Query(30, ge=1, description="今後何日先まで取得するか"),
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(10, ge=1, le=100, description="1ページあたりの件数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """今後接種予定の予防接種を取得"""
    vaccination_service = get_vaccination_service(db)
    return vaccination_service.get_upcoming_vaccinations(days_ahead, page, page_size)


@router.get("/search/", response_model=PaginatedResponse[VaccinationOut])
def search_vaccinations(
    q: str = Query(..., min_length=1, description="検索キーワード"),
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(10, ge=1, le=100, description="1ページあたりの件数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """予防接種記録を検索"""
    vaccination_service = get_vaccination_service(db)
    return vaccination_service.search_vaccinations(q, page, page_size)