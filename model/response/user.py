class UserResp:
    def __init__(self, user_id, name):
        self.id = user_id
        self.name = name

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }