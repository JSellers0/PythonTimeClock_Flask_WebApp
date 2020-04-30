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
        self.userid = user["userid"]
        self.user_name = user["user_name"]
        self.email = user["email"]
        self.reset_timelog_data()
        
    @property
    def id(self):
        return self

    def set_timelog_data(self, tl):
        self.clientid = tl["clientid"]
        self.client = tl["client_name"]
        self.projectid = tl["projectid"]
        self.project = tl["project_name"]
        self.start = tl["start"]

    def reset_timelog_data(self):
        self.timelogid = 0
        self.clientid = 0
        self.client = ""
        self.projectid = 0
        self.project = ""
        self.start = ""
        self.stopped = 0


