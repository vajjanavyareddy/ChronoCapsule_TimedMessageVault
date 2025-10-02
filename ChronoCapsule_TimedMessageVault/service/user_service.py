class UserService:
    def __init__(self, repository):
        self.repository = repository

    def create_user(self, user):
        self.repository.save(user)

    def get_user(self, user_id):
        return self.repository.find_by_id(user_id)

    def get_all_users(self):
        return self.repository.find_all()
