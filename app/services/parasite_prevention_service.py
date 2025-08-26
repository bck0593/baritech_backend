import uuid
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc

from app.models.parasite_prevention import ParasitePrevention
from app.schemas.parasite_prevention import ParasitePreventionCreate, ParasitePreventionUpdate, ParasitePreventionOut
from app.core.pagination import PaginatedResponse, paginate_query


class ParasitePreventionService:
    """寄生虫予防サービス層"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_parasite_prevention(self, prevention_data: ParasitePreventionCreate) -> ParasitePreventionOut:
        """寄生虫予防記録を作成"""
        prevention_dict = prevention_data.model_dump()
        prevention_dict["id"] = str(uuid.uuid4())
        prevention_dict["created_at"] = datetime.now()  # created_atを明示的に設定
        
        db_prevention = ParasitePrevention(**prevention_dict)
        self.db.add(db_prevention)
        self.db.commit()
        self.db.refresh(db_prevention)
        
        return ParasitePreventionOut.model_validate(db_prevention)
    
    def get_parasite_prevention(self, prevention_id: str) -> Optional[ParasitePreventionOut]:
        """寄生虫予防記録を ID で取得"""
        prevention = self.db.query(ParasitePrevention).filter(ParasitePrevention.id == prevention_id).first()
        return ParasitePreventionOut.model_validate(prevention) if prevention else None
    
    def get_parasite_preventions(
        self,
        page: int = 1,
        page_size: int = 10,
        dog_id: Optional[str] = None,
        product_name: Optional[str] = None,
        dosage: Optional[str] = None,
        administered_from: Optional[date] = None,
        administered_to: Optional[date] = None,
        due_from: Optional[date] = None,
        due_to: Optional[date] = None,
        sort_by: str = "administered_on",
        sort_order: str = "desc"
    ) -> PaginatedResponse[ParasitePreventionOut]:
        """寄生虫予防記録一覧を取得（フィルタ・ページネーション対応）"""
        
        # ベースクエリ
        query = self.db.query(ParasitePrevention)
        
        # フィルタリング
        filters = []
        
        if dog_id:
            filters.append(ParasitePrevention.dog_id == dog_id)
        
        if product_name:
            filters.append(ParasitePrevention.product_name.ilike(f"%{product_name}%"))
        
        if dosage:
            filters.append(ParasitePrevention.dosage.ilike(f"%{dosage}%"))
        
        if administered_from:
            filters.append(ParasitePrevention.administered_on >= administered_from)
        
        if administered_to:
            filters.append(ParasitePrevention.administered_on <= administered_to)
        
        if due_from:
            filters.append(ParasitePrevention.next_due_on >= due_from)
        
        if due_to:
            filters.append(ParasitePrevention.next_due_on <= due_to)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # ソート
        sort_column = getattr(ParasitePrevention, sort_by, None)
        if sort_column is not None:
            if sort_order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        else:
            # デフォルトソート: 投与日降順
            query = query.order_by(desc(ParasitePrevention.administered_on))
        
        # ページネーション
        return paginate_query(query, page, page_size, ParasitePreventionOut)
    
    def update_parasite_prevention(self, prevention_id: str, prevention_data: ParasitePreventionUpdate) -> Optional[ParasitePreventionOut]:
        """寄生虫予防記録を更新"""
        prevention = self.db.query(ParasitePrevention).filter(ParasitePrevention.id == prevention_id).first()
        if not prevention:
            return None
        
        update_data = prevention_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(prevention, field, value)
        
        self.db.commit()
        self.db.refresh(prevention)
        
        return ParasitePreventionOut.model_validate(prevention)
    
    def delete_parasite_prevention(self, prevention_id: str) -> bool:
        """寄生虫予防記録を削除"""
        prevention = self.db.query(ParasitePrevention).filter(ParasitePrevention.id == prevention_id).first()
        if not prevention:
            return False
        
        self.db.delete(prevention)
        self.db.commit()
        return True
    
    def get_parasite_preventions_by_dog(self, dog_id: str) -> List[ParasitePreventionOut]:
        """特定の犬の寄生虫予防記録をすべて取得"""
        preventions = (
            self.db.query(ParasitePrevention)
            .filter(ParasitePrevention.dog_id == dog_id)
            .order_by(desc(ParasitePrevention.administered_on))
            .all()
        )
        return [ParasitePreventionOut.model_validate(p) for p in preventions]
    
    def get_upcoming_parasite_preventions(
        self,
        days_ahead: int = 30,
        page: int = 1,
        page_size: int = 10
    ) -> PaginatedResponse[ParasitePreventionOut]:
        """今後投与予定の寄生虫予防を取得"""
        today = date.today()
        target_date = date.fromordinal(today.toordinal() + days_ahead)
        
        query = (
            self.db.query(ParasitePrevention)
            .filter(
                and_(
                    ParasitePrevention.next_due_on.is_not(None),
                    ParasitePrevention.next_due_on >= today,
                    ParasitePrevention.next_due_on <= target_date
                )
            )
            .order_by(asc(ParasitePrevention.next_due_on))
        )
        
        return paginate_query(query, page, page_size, ParasitePreventionOut)
    
    def search_parasite_preventions(
        self, 
        search_term: str,
        page: int = 1,
        page_size: int = 10
    ) -> PaginatedResponse[ParasitePreventionOut]:
        """寄生虫予防記録を検索（製品名、投与者、備考から検索）"""
        query = self.db.query(ParasitePrevention).filter(
            or_(
                ParasitePrevention.product_name.ilike(f"%{search_term}%"),
                ParasitePrevention.administered_by.ilike(f"%{search_term}%"),
                ParasitePrevention.notes.ilike(f"%{search_term}%"),
                ParasitePrevention.dosage.ilike(f"%{search_term}%")
            )
        ).order_by(desc(ParasitePrevention.administered_on))
        
        return paginate_query(query, page, page_size, ParasitePreventionOut)
    
    def get_parasite_preventions_by_product(
        self,
        product_name: str,
        page: int = 1,
        page_size: int = 10
    ) -> PaginatedResponse[ParasitePreventionOut]:
        """特定の製品の寄生虫予防記録を取得"""
        query = (
            self.db.query(ParasitePrevention)
            .filter(ParasitePrevention.product_name.ilike(f"%{product_name}%"))
            .order_by(desc(ParasitePrevention.administered_on))
        )
        
        return paginate_query(query, page, page_size, ParasitePreventionOut)


def get_parasite_prevention_service(db: Session) -> ParasitePreventionService:
    """寄生虫予防サービスのファクトリ関数"""
    return ParasitePreventionService(db)