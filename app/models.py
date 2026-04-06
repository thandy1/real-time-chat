from flask_login import UserMixin

class User(UserMixin):
    """Represents a user in the system. Inherits from UserMixin to get default implementations for Flask-Login."""
    def __init__(self, user_id, username, email):
        self.user_id = user_id
        self.username = username
        self.email = email

    def get_id(self):
        """Returns the unique identifier for the user, which Flask-Login uses to manage sessions. In this case, we return the user_id as a string."""
        return str(self.user_id)