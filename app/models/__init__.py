# SQLAlchemy Models - Import order is important to avoid circular dependencies

# Core models first (no relationships to other models)
from app.models.user import User, UserStatus, UserRole

# Primary entity models (depend on User)
from app.models.owner import Owner

# Secondary entity models (depend on Owner)
from app.models.dog import Dog

# Business record models (depend on Dog and User)
from app.models.booking import Booking
from app.models.diary_entry import DiaryEntry
from app.models.health_record import HealthRecord
from app.models.meal import Meal
from app.models.dog_evaluation import DogEvaluation

# Community models (depend on User)
from app.models.post import Post
from app.models.comment import Comment
from app.models.like import Like
from app.models.notification import Notification

# Event models (depend on User, Owner, Dog)
from app.models.walk_event import WalkEvent
from app.models.walk_participant import WalkParticipant

# Medical/certificate models (standalone)
from app.models.vaccination import Vaccination
from app.models.parasite_prevention import ParasitePrevention
from app.models.certificate import Certificate

# Export all models
__all__ = [
    # Core models
    "User", "UserStatus", "UserRole",
    "Owner",
    "Dog",
    
    # Business records
    "Booking", "DiaryEntry", "HealthRecord", "Meal", "DogEvaluation",
    
    # Community
    "Post", "Comment", "Like", "Notification",
    
    # Events
    "WalkEvent", "WalkParticipant",
    
    # Medical/certificates
    "Vaccination", "ParasitePrevention", "Certificate"
]