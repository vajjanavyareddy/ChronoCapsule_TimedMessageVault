from model.user import User
import uuid

class UserController:
    def __init__(self, service):
        self.service = service

    def create_user_ui(self):
        
        name = input("Enter Name: ")
        email = input("Enter Email: ")
        user = User(None, name, email)  # Pass None for id
        self.service.create_user(user)
        print("User created successfully!")


    def list_users_ui(self):
        users = self.service.get_all_users()
        if not users:
            print("No users found!")
        for u in users:
            print(f"ID: {u.id}, Name: {u.name}, Email: {u.email}")
