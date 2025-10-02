# deliver_worker.py
import os
from repository.user_repository import UserRepository
from repository.capsule_repository import CapsuleRepository
from service.user_service import UserService
from service.capsule_service import CapsuleService

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

user_repo = UserRepository(SUPABASE_URL, SUPABASE_KEY)
cap_repo = CapsuleRepository(SUPABASE_URL, SUPABASE_KEY)
user_service = UserService(user_repo)
cap_service = CapsuleService(cap_repo, user_service)

if __name__ == '__main__':
    cap_service.deliver_capsules()
