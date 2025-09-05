from fastapi import APIRouter

from app.api.v1.routers import auth, dogs, bookings, diary_entries, health_records, meals, walk_events, walk_participants, dog_evaluations, posts, comments, likes, notifications, vaccinations, parasite_preventions, certificates, owners

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(owners.router, prefix="/owners", tags=["owners"])
api_router.include_router(dogs.router, prefix="/dogs", tags=["dogs"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
api_router.include_router(diary_entries.router, prefix="/diary-entries", tags=["diary-entries"])
api_router.include_router(health_records.router, prefix="/health-records", tags=["health-records"])
api_router.include_router(meals.router, prefix="/meals", tags=["meals"])
api_router.include_router(walk_events.router, prefix="/walk-events", tags=["walk-events"])
api_router.include_router(walk_participants.router, prefix="/walk-participants", tags=["walk-participants"])
api_router.include_router(dog_evaluations.router, prefix="/dog-evaluations", tags=["dog-evaluations"])
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(comments.router, prefix="/posts", tags=["comments"])
api_router.include_router(comments.router, prefix="/comments", tags=["comments"])
api_router.include_router(likes.router, prefix="/posts", tags=["likes"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(vaccinations.router, prefix="/vaccinations", tags=["vaccinations"])
api_router.include_router(parasite_preventions.router, prefix="/parasite-preventions", tags=["parasite-preventions"])
api_router.include_router(certificates.router, prefix="/certificates", tags=["certificates"])