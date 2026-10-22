from app.src.domain.entities.user import User
from app.src.domain.exceptions import UserAlreadyExistsError
from app.src.domain.repositories.user_repository import UserRepository


class CreateUser:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, user: User) -> User:
        existing = self.user_repository.get_by_identification(
            user.identification_number
        )

        if existing is not None:
            raise UserAlreadyExistsError(user.identification_number)

        return self.user_repository.create(user)
