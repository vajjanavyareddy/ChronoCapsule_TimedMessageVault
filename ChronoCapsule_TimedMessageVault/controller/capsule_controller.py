# controller/capsule_controller.py
from datetime import datetime, timezone
from model.capsule import Capsule
import uuid

class CapsuleController:
    def __init__(self, service):
        self.service = service

    def create_capsule_ui(self):
        users = self.service.user_service.get_all_users()
        if not users:
            print("No users found! Please create a user first.")
            return

        print("Select user for this capsule:")
        for idx, u in enumerate(users):
            print(f"{idx+1}. {u.name} ({u.email})")
        choice = int(input("Enter choice: ")) - 1
        creator_id = users[choice].id

        title = input("Enter Capsule Title: ")
        message = input("Enter Capsule Message: ")
        time_str = input("Enter scheduled time (YYYY-MM-DD HH:MM): ")

        
        scheduled_time_local = datetime.strptime(time_str, "%Y-%m-%d %H:%M")

       
        scheduled_time_utc = scheduled_time_local.replace(tzinfo=timezone.utc)

        capsule = Capsule(
            None,
            title,
            message,
            creator_id,
            scheduled_time_utc
        )
        self.service.create_capsule(capsule)
        print("Capsule created successfully!")

    def deliver_capsules_ui(self):
        """
        Fetch pending capsules and deliver only if scheduled time has arrived.
        Converts UTC stored time to local time for comparison.
        """
        self.service.deliver_capsules()
