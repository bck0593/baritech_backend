import uuid
from datetime import date, datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc

from app.models.health_record import HealthRecord
from app.schemas.health_record import HealthRecordCreate, HealthRecordUpdate, HealthRecordOut
from app.core.pagination import PaginatedResponse, paginate_query


class HealthRecordService:
    """健康記録サービス層"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_health_record(self, record_data: HealthRecordCreate) -> HealthRecordOut:
        """健康記録を作成"""
        record_dict = record_data.model_dump()
        record_dict["id"] = str(uuid.uuid4())
        
        db_record = HealthRecord(**record_dict)
        self.db.add(db_record)
        self.db.commit()
        self.db.refresh(db_record)
        
        return HealthRecordOut.model_validate(db_record)
    
    def get_health_record(self, record_id: str) -> Optional[HealthRecordOut]:
        """健康記録を ID で取得"""
        record = self.db.query(HealthRecord).filter(HealthRecord.id == record_id).first()
        return HealthRecordOut.model_validate(record) if record else None
    
    def get_health_records(
        self,
        page: int = 1,
        page_size: int = 10,
        dog_id: Optional[str] = None,
        record_date_from: Optional[date] = None,
        record_date_to: Optional[date] = None,
        weight_min: Optional[float] = None,
        weight_max: Optional[float] = None,
        temperature_min: Optional[float] = None,
        temperature_max: Optional[float] = None,
        sort_by: str = "record_date",
        sort_order: str = "desc"
    ) -> PaginatedResponse[HealthRecordOut]:
        """健康記録一覧を取得（フィルタ・ページネーション対応）"""
        
        # ベースクエリ
        query = self.db.query(HealthRecord)
        
        # フィルタリング
        filters = []
        
        if dog_id:
            filters.append(HealthRecord.dog_id == dog_id)
        
        if record_date_from:
            filters.append(HealthRecord.record_date >= record_date_from)
        
        if record_date_to:
            filters.append(HealthRecord.record_date <= record_date_to)
        
        if weight_min:
            filters.append(HealthRecord.weight_kg >= weight_min)
        
        if weight_max:
            filters.append(HealthRecord.weight_kg <= weight_max)
        
        if temperature_min:
            filters.append(HealthRecord.temperature_c >= temperature_min)
        
        if temperature_max:
            filters.append(HealthRecord.temperature_c <= temperature_max)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # ソート
        sort_column = getattr(HealthRecord, sort_by, None)
        if sort_column is not None:
            if sort_order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        else:
            # デフォルトソート: 記録日降順
            query = query.order_by(desc(HealthRecord.record_date))
        
        # ページネーション
        return paginate_query(query, page, page_size, HealthRecordOut)
    
    def update_health_record(self, record_id: str, record_data: HealthRecordUpdate) -> Optional[HealthRecordOut]:
        """健康記録を更新"""
        record = self.db.query(HealthRecord).filter(HealthRecord.id == record_id).first()
        if not record:
            return None
        
        update_data = record_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(record, field, value)
        
        self.db.commit()
        self.db.refresh(record)
        
        return HealthRecordOut.model_validate(record)
    
    def delete_health_record(self, record_id: str) -> bool:
        """健康記録を削除"""
        record = self.db.query(HealthRecord).filter(HealthRecord.id == record_id).first()
        if not record:
            return False
        
        self.db.delete(record)
        self.db.commit()
        return True
    
    def get_health_records_by_dog(self, dog_id: str) -> List[HealthRecordOut]:
        """特定の犬の健康記録をすべて取得"""
        records = (
            self.db.query(HealthRecord)
            .filter(HealthRecord.dog_id == dog_id)
            .order_by(desc(HealthRecord.record_date))
            .all()
        )
        return [HealthRecordOut.model_validate(r) for r in records]
    
    def get_recent_health_records(
        self,
        days: int = 30,
        page: int = 1,
        page_size: int = 10
    ) -> PaginatedResponse[HealthRecordOut]:
        """最近の健康記録を取得"""
        from datetime import timedelta
        cutoff_date = date.today() - timedelta(days=days)
        
        query = (
            self.db.query(HealthRecord)
            .filter(HealthRecord.record_date >= cutoff_date)
            .order_by(desc(HealthRecord.record_date))
        )
        
        return paginate_query(query, page, page_size, HealthRecordOut)
    
    def search_health_records(
        self, 
        search_term: str,
        page: int = 1,
        page_size: int = 10
    ) -> PaginatedResponse[HealthRecordOut]:
        """健康記録を検索（備考から検索）"""
        query = self.db.query(HealthRecord).filter(
            HealthRecord.notes.ilike(f"%{search_term}%")
        ).order_by(desc(HealthRecord.record_date))
        
        return paginate_query(query, page, page_size, HealthRecordOut)


def get_health_record_service(db: Session) -> HealthRecordService:
    """健康記録サービスのファクトリ関数"""
    return HealthRecordService(db)