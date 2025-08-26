from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.deps import get_db, get_current_user
from app.models.user import User, UserRole
from app.models.post import Post, PostType
from app.schemas.post import PostCreate, PostUpdate, PostOut
from app.schemas.common import PaginatedResponse

router = APIRouter()


def can_view_post(post: Post, current_user: User) -> bool:
    """Check if user can view a post"""
    # Public posts can be viewed by anyone
    if post.is_public:
        return True
    # Private posts can only be viewed by author or admin
    if post.author_user_id == current_user.id:
        return True
    if current_user.role == UserRole.ADMIN or current_user.role == UserRole.SUPER_ADMIN:
        return True
    return False


def can_modify_post(post: Post, current_user: User) -> bool:
    """Check if user can modify a post"""
    # Only author can modify (except delete)
    return post.author_user_id == current_user.id


def can_delete_post(post: Post, current_user: User) -> bool:
    """Check if user can delete a post"""
    # Author or admin can delete
    if post.author_user_id == current_user.id:
        return True
    if current_user.role == UserRole.ADMIN or current_user.role == UserRole.SUPER_ADMIN:
        return True
    return False


@router.post("/", response_model=PostOut)
def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new post (all authenticated users)"""
    
    # Create post with current user as author
    post = Post(
        author_user_id=current_user.id,
        title=post_data.title,
        content=post_data.content,
        post_type=post_data.post_type,
        photos_json=post_data.photos_json,
        is_public=post_data.is_public
    )
    
    db.add(post)
    db.commit()
    db.refresh(post)
    
    # Add author name for response
    post_out = PostOut.from_orm(post)
    post_out.author_name = current_user.name
    
    return post_out


@router.get("/", response_model=PaginatedResponse[PostOut])
def get_posts(
    author_user_id: Optional[str] = Query(None, description="Filter by author user ID"),
    post_type: Optional[PostType] = Query(None, description="Filter by post type"),
    is_public: Optional[bool] = Query(None, description="Filter by public/private"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get posts list with filtering and pagination"""
    
    query = db.query(Post).join(User, Post.author_user_id == User.id)
    
    # Apply filters
    if author_user_id:
        query = query.filter(Post.author_user_id == author_user_id)
    
    if post_type:
        query = query.filter(Post.post_type == post_type)
    
    if is_public is not None:
        query = query.filter(Post.is_public == is_public)
    
    # Apply visibility rules
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        # Non-admin users can only see public posts or their own posts
        query = query.filter(
            (Post.is_public == True) | (Post.author_user_id == current_user.id)
        )
    
    # Order by creation date (newest first)
    query = query.order_by(Post.created_at.desc())
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    posts = query.offset((page - 1) * size).limit(size).all()
    
    # Convert to response format with author names
    post_items = []
    for post in posts:
        post_out = PostOut.from_orm(post)
        post_out.author_name = post.author.name
        post_items.append(post_out)
    
    return PaginatedResponse(
        items=post_items,
        total=total,
        page=page,
        per_page=size,
        pages=(total + size - 1) // size
    )


@router.get("/{post_id}", response_model=PostOut)
def get_post(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a single post by ID"""
    
    post = db.query(Post).join(User, Post.author_user_id == User.id).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if not can_view_post(post, current_user):
        raise HTTPException(status_code=403, detail="Not authorized to view this post")
    
    # Add author name for response
    post_out = PostOut.from_orm(post)
    post_out.author_name = post.author.name
    
    return post_out


@router.patch("/{post_id}", response_model=PostOut)
def update_post(
    post_id: str,
    post_data: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a post (author only)"""
    
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if not can_modify_post(post, current_user):
        raise HTTPException(status_code=403, detail="Not authorized to modify this post")
    
    # Update fields
    update_data = post_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)
    
    db.commit()
    db.refresh(post)
    
    # Add author name for response
    post_out = PostOut.from_orm(post)
    post_out.author_name = current_user.name
    
    return post_out


@router.delete("/{post_id}")
def delete_post(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a post (author or admin)"""
    
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if not can_delete_post(post, current_user):
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    
    db.delete(post)
    db.commit()
    
    return {"detail": "Post deleted successfully"}