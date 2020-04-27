from flask_login import UserMixin

class MyUser(UserMixin):
    def __init__(self, user=None):
        if user:
            self.userid = user["userid"]
            self.user_name = user["user_name"]
            self.email = user["email"]
            
    @property
    def id(self):
        return self.user_name


