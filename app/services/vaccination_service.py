import uuid
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc

from app.models.vaccination import Vaccination
from app.schemas.vaccination import VaccinationCreate, VaccinationUpdate, VaccinationOut
from app.core.pagination import PaginatedResponse, paginate_query


class VaccinationService:
    """予防接種サービス層"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_vaccination(self, vaccination_data: VaccinationCreate) -> VaccinationOut:
        """予防接種記録を作成"""
        vaccination_dict = vaccination_data.model_dump()
        vaccination_dict["id"] = str(uuid.uuid4())
        vaccination_dict["created_at"] = datetime.now()  # created_atを明示的に設定
        
        db_vaccination = Vaccination(**vaccination_dict)
        self.db.add(db_vaccination)
        self.db.commit()
        self.db.refresh(db_vaccination)
        
        return VaccinationOut.model_validate(db_vaccination)
    
    def get_vaccination(self, vaccination_id: str) -> Optional[VaccinationOut]:
        """予防接種記録を ID で取得"""
        vaccination = self.db.query(Vaccination).filter(Vaccination.id == vaccination_id).first()
        return VaccinationOut.model_validate(vaccination) if vaccination else None
    
    def get_vaccinations(
        self,
        page: int = 1,
        page_size: int = 10,
        dog_id: Optional[str] = None,
        vaccine_name: Optional[str] = None,
        administered_from: Optional[date] = None,
        administered_to: Optional[date] = None,
        due_from: Optional[date] = None,
        due_to: Optional[date] = None,
        sort_by: str = "administered_on",
        sort_order: str = "desc"
    ) -> PaginatedResponse[VaccinationOut]:
        """予防接種記録一覧を取得（フィルタ・ページネーション対応）"""
        
        # ベースクエリ
        query = self.db.query(Vaccination)
        
        # フィルタリング
        filters = []
        
        if dog_id:
            filters.append(Vaccination.dog_id == dog_id)
        
        if vaccine_name:
            filters.append(Vaccination.vaccine_name.ilike(f"%{vaccine_name}%"))
        
        if administered_from:
            filters.append(Vaccination.administered_on >= administered_from)
        
        if administered_to:
            filters.append(Vaccination.administered_on <= administered_to)
        
        if due_from:
            filters.append(Vaccination.next_due_on >= due_from)
        
        if due_to:
            filters.append(Vaccination.next_due_on <= due_to)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # ソート
        sort_column = getattr(Vaccination, sort_by, None)
        if sort_column is not None:
            if sort_order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        else:
            # デフォルトソート: 接種日降順
            query = query.order_by(desc(Vaccination.administered_on))
        
        # ページネーション
        return paginate_query(query, page, page_size, VaccinationOut)
    
    def update_vaccination(self, vaccination_id: str, vaccination_data: VaccinationUpdate) -> Optional[VaccinationOut]:
        """予防接種記録を更新"""
        vaccination = self.db.query(Vaccination).filter(Vaccination.id == vaccination_id).first()
        if not vaccination:
            return None
        
        update_data = vaccination_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(vaccination, field, value)
        
        self.db.commit()
        self.db.refresh(vaccination)
        
        return VaccinationOut.model_validate(vaccination)
    
    def delete_vaccination(self, vaccination_id: str) -> bool:
        """予防接種記録を削除"""
        vaccination = self.db.query(Vaccination).filter(Vaccination.id == vaccination_id).first()
        if not vaccination:
            return False
        
        self.db.delete(vaccination)
        self.db.commit()
        return True
    
    def get_vaccinations_by_dog(self, dog_id: str) -> List[VaccinationOut]:
        """特定の犬の予防接種記録をすべて取得"""
        vaccinations = (
            self.db.query(Vaccination)
            .filter(Vaccination.dog_id == dog_id)
            .order_by(desc(Vaccination.administered_on))
            .all()
        )
        return [VaccinationOut.model_validate(v) for v in vaccinations]
    
    def get_upcoming_vaccinations(
        self,
        days_ahead: int = 30,
        page: int = 1,
        page_size: int = 10
    ) -> PaginatedResponse[VaccinationOut]:
        """今後接種予定の予防接種を取得"""
        today = date.today()
        target_date = date.fromordinal(today.toordinal() + days_ahead)
        
        query = (
            self.db.query(Vaccination)
            .filter(
                and_(
                    Vaccination.next_due_on.is_not(None),
                    Vaccination.next_due_on >= today,
                    Vaccination.next_due_on <= target_date
                )
            )
            .order_by(asc(Vaccination.next_due_on))
        )
        
        return paginate_query(query, page, page_size, VaccinationOut)
    
    def search_vaccinations(
        self, 
        search_term: str,
        page: int = 1,
        page_size: int = 10
    ) -> PaginatedResponse[VaccinationOut]:
        """予防接種記録を検索（ワクチン名、実施者、備考から検索）"""
        query = self.db.query(Vaccination).filter(
            or_(
                Vaccination.vaccine_name.ilike(f"%{search_term}%"),
                Vaccination.administered_by.ilike(f"%{search_term}%"),
                Vaccination.notes.ilike(f"%{search_term}%")
            )
        ).order_by(desc(Vaccination.administered_on))
        
        return paginate_query(query, page, page_size, VaccinationOut)


def get_vaccination_service(db: Session) -> VaccinationService:
    """予防接種サービスのファクトリ関数"""
    return VaccinationService(db)