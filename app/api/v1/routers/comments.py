from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List

from app.core.deps import get_db, get_current_user
from app.models.user import User, UserRole
from app.models.post import Post
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate, CommentOut

router = APIRouter()


def can_view_post(post: Post, current_user: User) -> bool:
    """Check if user can view a post and its comments"""
    # Public posts can be viewed by anyone
    if post.is_public:
        return True
    # Private posts can only be viewed by author or admin
    if post.author_user_id == current_user.id:
        return True
    if current_user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        return True
    return False


def can_delete_comment(comment: Comment, current_user: User) -> bool:
    """Check if user can delete a comment"""
    # Author or admin can delete
    if comment.author_user_id == current_user.id:
        return True
    if current_user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        return True
    return False


@router.post("/{post_id}/comments", response_model=CommentOut)
def create_comment(
    post_id: str = Path(..., description="Post ID"),
    comment_data: CommentCreate = ...,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new comment for a post"""
    
    # Verify post exists and user can access it
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if not can_view_post(post, current_user):
        raise HTTPException(status_code=403, detail="Not authorized to comment on this post")
    
    # If parent_comment_id is provided, verify it exists and belongs to the same post
    if comment_data.parent_comment_id:
        parent_comment = db.query(Comment).filter(
            Comment.id == comment_data.parent_comment_id,
            Comment.post_id == post_id,
            Comment.is_deleted == False
        ).first()
        if not parent_comment:
            raise HTTPException(status_code=404, detail="Parent comment not found")
    
    # Create comment
    comment = Comment(
        post_id=post_id,
        author_user_id=current_user.id,
        content=comment_data.content,
        parent_comment_id=comment_data.parent_comment_id
    )
    
    db.add(comment)
    
    # Update post comment count
    post.comment_count += 1
    
    db.commit()
    db.refresh(comment)
    
    # Add author name for response
    comment_out = CommentOut.from_orm(comment)
    comment_out.author_name = current_user.name
    
    return comment_out


@router.get("/{post_id}/comments", response_model=List[CommentOut])
def get_comments(
    post_id: str = Path(..., description="Post ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all comments for a post (hierarchical structure)"""
    
    # Verify post exists and user can access it
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if not can_view_post(post, current_user):
        raise HTTPException(status_code=403, detail="Not authorized to view comments on this post")
    
    # Get all non-deleted comments for the post
    comments = db.query(Comment).join(User, Comment.author_user_id == User.id).filter(
        Comment.post_id == post_id,
        Comment.is_deleted == False
    ).order_by(Comment.created_at.asc()).all()
    
    # Convert to response format with author names
    comment_items = []
    for comment in comments:
        comment_out = CommentOut.from_orm(comment)
        comment_out.author_name = comment.author.name
        comment_items.append(comment_out)
    
    return comment_items


@router.delete("/{comment_id}")
def delete_comment(
    comment_id: str = Path(..., description="Comment ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a comment (logical deletion)"""
    
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if comment.is_deleted:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if not can_delete_comment(comment, current_user):
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    
    # Logical deletion
    comment.is_deleted = True
    
    # Update post comment count
    post = db.query(Post).filter(Post.id == comment.post_id).first()
    if post:
        post.comment_count = max(0, post.comment_count - 1)
    
    db.commit()
    
    return {"detail": "Comment deleted successfully"}