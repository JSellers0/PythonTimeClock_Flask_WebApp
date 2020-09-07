from flask_login import UserMixin

class UserManager():
    def __init__(self):
        self.users = {}

    def get_user(self, email):
        try:
            return self.users[email]
        except KeyError:
            return None

    def add_user(self, email, user):
        self.users[email] = user


class MyUser():
    def __init__(self, user):
        self.userid = user.get("userid")
        self.user_name = user.get("user_name")
        self.email = user.get("email")
        self.timezone = user.get("timezone")


