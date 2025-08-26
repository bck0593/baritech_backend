from typing import TypeVar, Generic, List
from pydantic import BaseModel
from sqlalchemy.orm import Query
import math

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """ページネーション付きレスポンス"""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


def paginate_query(
    query: Query, 
    page: int, 
    page_size: int, 
    response_model: type
) -> PaginatedResponse:
    """SQLAlchemyクエリをページネーション"""
    
    # 総件数取得
    total = query.count()
    
    # ページネーション計算
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    offset = (page - 1) * page_size
    
    # データ取得
    items = query.offset(offset).limit(page_size).all()
    
    # レスポンスモデルに変換
    response_items = [response_model.model_validate(item) for item in items]
    
    return PaginatedResponse(
        items=response_items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )