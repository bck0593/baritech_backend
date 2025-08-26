from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from typing import List

from app.core.deps import get_db, get_current_user
from app.models.user import User, UserRole
from app.models.post import Post
from app.models.like import Like
from app.schemas.like import LikeCreate, LikeOut

router = APIRouter()


def can_view_post(post: Post, current_user: User) -> bool:
    """Check if user can view a post and its likes"""
    # Public posts can be viewed by anyone
    if post.is_public:
        return True
    # Private posts can only be viewed by author or admin
    if post.author_user_id == current_user.id:
        return True
    if current_user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        return True
    return False


@router.post("/{post_id}/likes", response_model=LikeOut)
def create_like(
    post_id: str = Path(..., description="Post ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a like to a post"""
    
    # Verify post exists and user can access it
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if not can_view_post(post, current_user):
        raise HTTPException(status_code=403, detail="Not authorized to like this post")
    
    # Check if user already liked this post
    existing_like = db.query(Like).filter(
        and_(Like.post_id == post_id, Like.user_id == current_user.id)
    ).first()
    
    if existing_like:
        raise HTTPException(status_code=409, detail="You have already liked this post")
    
    # Create like
    like = Like(
        post_id=post_id,
        user_id=current_user.id
    )
    
    try:
        db.add(like)
        
        # Update post like count
        post.like_count += 1
        
        db.commit()
        db.refresh(like)
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="You have already liked this post")
    
    # Add user name for response
    like_out = LikeOut.from_orm(like)
    like_out.user_name = current_user.name
    
    return like_out


@router.delete("/{post_id}/likes")
def delete_like(
    post_id: str = Path(..., description="Post ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a like from a post"""
    
    # Verify post exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Find user's like on this post
    like = db.query(Like).filter(
        and_(Like.post_id == post_id, Like.user_id == current_user.id)
    ).first()
    
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")
    
    # Delete like and update post count
    db.delete(like)
    post.like_count = max(0, post.like_count - 1)
    
    db.commit()
    
    return {"detail": "Like removed successfully"}


@router.get("/{post_id}/likes", response_model=List[LikeOut])
def get_likes(
    post_id: str = Path(..., description="Post ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all likes for a post"""
    
    # Verify post exists and user can access it
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if not can_view_post(post, current_user):
        raise HTTPException(status_code=403, detail="Not authorized to view likes on this post")
    
    # Get all likes for the post
    likes = db.query(Like).join(User, Like.user_id == User.id).filter(
        Like.post_id == post_id
    ).order_by(Like.created_at.desc()).all()
    
    # Convert to response format with user names
    like_items = []
    for like in likes:
        like_out = LikeOut.from_orm(like)
        like_out.user_name = like.user.name
        like_items.append(like_out)
    
    return like_items