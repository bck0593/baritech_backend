from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_active_user, get_current_admin_user
from app.core.pagination import PaginatedResponse
from app.models.user import User
from app.schemas.parasite_prevention import ParasitePreventionCreate, ParasitePreventionUpdate, ParasitePreventionOut
from app.services.parasite_prevention_service import get_parasite_prevention_service, ParasitePreventionService

router = APIRouter()


@router.post("/", response_model=ParasitePreventionOut, status_code=status.HTTP_201_CREATED)
def create_parasite_prevention(
    prevention_data: ParasitePreventionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # 管理者のみ作成可能
):
    """寄生虫予防記録を作成"""
    prevention_service = get_parasite_prevention_service(db)
    return prevention_service.create_parasite_prevention(prevention_data)


@router.get("/{prevention_id}", response_model=ParasitePreventionOut)
def get_parasite_prevention(
    prevention_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """寄生虫予防記録を ID で取得"""
    prevention_service = get_parasite_prevention_service(db)
    prevention = prevention_service.get_parasite_prevention(prevention_id)
    
    if not prevention:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parasite prevention record not found"
        )
    
    return prevention


@router.get("/", response_model=PaginatedResponse[ParasitePreventionOut])
def list_parasite_preventions(
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(10, ge=1, le=100, description="1ページあたりの件数"),
    dog_id: Optional[str] = Query(None, description="犬ID"),
    product_name: Optional[str] = Query(None, description="製品名（部分一致）"),
    dosage: Optional[str] = Query(None, description="投与量（部分一致）"),
    administered_from: Optional[date] = Query(None, description="投与日（開始）"),
    administered_to: Optional[date] = Query(None, description="投与日（終了）"),
    due_from: Optional[date] = Query(None, description="次回予定日（開始）"),
    due_to: Optional[date] = Query(None, description="次回予定日（終了）"),
    sort_by: str = Query("administered_on", description="ソートフィールド"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="ソート順序"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """寄生虫予防記録一覧を取得（フィルタ・ページネーション対応）"""
    prevention_service = get_parasite_prevention_service(db)
    
    return prevention_service.get_parasite_preventions(
        page=page,
        page_size=page_size,
        dog_id=dog_id,
        product_name=product_name,
        dosage=dosage,
        administered_from=administered_from,
        administered_to=administered_to,
        due_from=due_from,
        due_to=due_to,
        sort_by=sort_by,
        sort_order=sort_order
    )


@router.put("/{prevention_id}", response_model=ParasitePreventionOut)
def update_parasite_prevention(
    prevention_id: str,
    prevention_data: ParasitePreventionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # 管理者のみ更新可能
):
    """寄生虫予防記録を更新"""
    prevention_service = get_parasite_prevention_service(db)
    prevention = prevention_service.update_parasite_prevention(prevention_id, prevention_data)
    
    if not prevention:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parasite prevention record not found"
        )
    
    return prevention


@router.delete("/{prevention_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_parasite_prevention(
    prevention_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)  # 管理者のみ削除可能
):
    """寄生虫予防記録を削除"""
    prevention_service = get_parasite_prevention_service(db)
    success = prevention_service.delete_parasite_prevention(prevention_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parasite prevention record not found"
        )


@router.get("/by-dog/{dog_id}", response_model=list[ParasitePreventionOut])
def get_parasite_preventions_by_dog(
    dog_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """特定の犬の寄生虫予防記録をすべて取得"""
    prevention_service = get_parasite_prevention_service(db)
    return prevention_service.get_parasite_preventions_by_dog(dog_id)


@router.get("/upcoming/", response_model=PaginatedResponse[ParasitePreventionOut])
def get_upcoming_parasite_preventions(
    days_ahead: int = Query(30, ge=1, description="今後何日先まで取得するか"),
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(10, ge=1, le=100, description="1ページあたりの件数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """今後投与予定の寄生虫予防を取得"""
    prevention_service = get_parasite_prevention_service(db)
    return prevention_service.get_upcoming_parasite_preventions(days_ahead, page, page_size)


@router.get("/search/", response_model=PaginatedResponse[ParasitePreventionOut])
def search_parasite_preventions(
    q: str = Query(..., min_length=1, description="検索キーワード"),
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(10, ge=1, le=100, description="1ページあたりの件数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """寄生虫予防記録を検索"""
    prevention_service = get_parasite_prevention_service(db)
    return prevention_service.search_parasite_preventions(q, page, page_size)


@router.get("/by-product/{product_name}", response_model=PaginatedResponse[ParasitePreventionOut])
def get_parasite_preventions_by_product(
    product_name: str,
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(10, ge=1, le=100, description="1ページあたりの件数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """特定の製品の寄生虫予防記録を取得"""
    prevention_service = get_parasite_prevention_service(db)
    return prevention_service.get_parasite_preventions_by_product(product_name, page, page_size)