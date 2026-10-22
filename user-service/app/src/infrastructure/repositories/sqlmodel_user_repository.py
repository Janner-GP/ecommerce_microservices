from sqlmodel import select

from app.src.domain.entities.user import User
from app.src.domain.models.user import User as UserModel
from app.src.domain.repositories.user_repository import UserRepository


class SQLModelUserRepository(UserRepository):
    def __init__(self, session):
        self.session = session

    def get_by_id(self, user_id):
        model = self.session.get(UserModel, user_id)

        if model is None:
            return None

        return to_domain(model)

    def get_by_identification(self, identification_number):
        statement = select(UserModel).where(
            UserModel.identification_number == identification_number
        )
        model = self.session.exec(statement).first()

        if model is None:
            return None

        return to_domain(model)

    def create(self, user):
        model = UserModel(
            id=user.id,
            name=user.name,
            identification_type=user.identification_type,
            identification_number=user.identification_number,
            birthday_date=user.birthday_date,
            status=user.status,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        self.session.add(model)

        # flush envía el INSERT pero NO lo confirma: el commit lo hace get_session.
        self.session.flush()
        self.session.refresh(model)

        return to_domain(model)


def to_domain(model):
    """Convierte el modelo de SQLModel en la entidad de dominio."""
    return User(
        id=model.id,
        name=model.name,
        identification_type=model.identification_type,
        identification_number=model.identification_number,
        birthday_date=model.birthday_date,
        status=model.status,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
