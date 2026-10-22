class UserAlreadyExistsError(Exception):
    def __init__(self, identification_number: str):
        super().__init__(
            f"Ya existe un usuario con la identificación {identification_number}"
        )


class UserNotFoundError(Exception):
    def __init__(self, user_id):
        super().__init__(f"No existe el usuario {user_id}")
