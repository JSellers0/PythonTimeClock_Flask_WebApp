from flask_login import UserMixin

class UserManager():
    def __init__(self):
        self.users = {}

    def get_user(self, userid):
        try:
            return self.users[userid]
        except KeyError:
            return None

    def add_user(self, userid, user):
        self.users[userid] = user


class MyUser(UserMixin):
    def __init__(self, user):
        self.userid = user.get("userid")
        self.user_name = user.get("user_name")
        self.email = user.get("email")
        self.timezone = user.get("timezone")
        
    @property
    def id(self):
        return self


