# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.session import Base  # noqa
from app.models.user import User  # noqa
from app.models.owner import Owner  # noqa
from app.models.dog import Dog  # noqa
from app.models.booking import Booking  # noqa
from app.models.diary_entry import DiaryEntry  # noqa
from app.models.walk_event import WalkEvent  # noqa
from app.models.walk_participant import WalkParticipant  # noqa
from app.models.walk_report import WalkReport  # noqa
from app.models.dog_evaluation import DogEvaluation  # noqa
from app.models.meal import Meal  # noqa
from app.models.health_record import HealthRecord  # noqa
from app.models.post import Post  # noqa
from app.models.comment import Comment  # noqa
from app.models.like import Like  # noqa
from app.models.notification import Notification  # noqa
from app.models.vaccination import Vaccination  # noqa
from app.models.parasite_prevention import ParasitePrevention  # noqa
from app.models.certificate import Certificate  # noqa