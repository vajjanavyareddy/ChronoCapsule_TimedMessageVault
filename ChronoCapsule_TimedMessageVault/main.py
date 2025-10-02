# main.py
from repository.user_repository import UserRepository
from repository.capsule_repository import CapsuleRepository
from service.user_service import UserService
from service.capsule_service import CapsuleService
from controller.user_controller import UserController
from controller.capsule_controller import CapsuleController
from threading import Thread
import time

SUPABASE_URL = "https://imrmwssaijnzjodkxxbt.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imltcm13c3NhaWpuempvZGt4eGJ0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxNzE3NjUsImV4cCI6MjA3Mzc0Nzc2NX0.VfwrhUAGb2xC1oleAvfry8pWYItvzxzhz4NS5CyiuaQ"

def auto_deliver(controller):
    """
    Background thread to auto-deliver capsules every 60 seconds.
    """
    while True:
        controller.deliver_capsules_ui()
        time.sleep(60)  

def main():
   
    user_repo = UserRepository(SUPABASE_URL, SUPABASE_KEY)
    capsule_repo = CapsuleRepository(SUPABASE_URL, SUPABASE_KEY)

    # Initialize services
    user_service = UserService(user_repo)
    capsule_service = CapsuleService(capsule_repo, user_service)

    # Initialize controllers
    user_controller = UserController(user_service)
    capsule_controller = CapsuleController(capsule_service)

    
    Thread(target=auto_deliver, args=(capsule_controller,), daemon=True).start()

    
    while True:
        print("\n ---CHRONOCAPSULE MENU---")
        print("1. Create User")
        print("2. List Users")
        print("3. Create Capsule")
        print("4. Deliver Capsules")
        print("5. Exit")
        choice = input("Enter choice: ").strip()

        if choice == '1':
            user_controller.create_user_ui()
        elif choice == '2':
            user_controller.list_users_ui()
        elif choice == '3':
            capsule_controller.create_capsule_ui()
        elif choice == '4':
            capsule_controller.deliver_capsules_ui()
        elif choice == '5':
            print("Exiting ChronoCapsule. Goodbye!")
            break
        else:
            print("Invalid choice! Please enter a number between 1 and 5.")

if __name__ == "__main__":
    main()
