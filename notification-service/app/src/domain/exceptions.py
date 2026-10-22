class InvalidNotificationError(Exception):
    pass


class NotificationNotFoundError(Exception):
    def __init__(self, notification_id):
        super().__init__(f"No existe la notificación {notification_id}")
