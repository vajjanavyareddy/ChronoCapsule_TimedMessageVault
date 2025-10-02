from datetime import datetime

class CapsuleService:
    def __init__(self, capsule_repo, user_service):
        self.repository = capsule_repo
        self.user_service = user_service

    def create_capsule(self, capsule):
        self.repository.save(capsule)

    def deliver_capsules(self):
        pending = self.repository.find_all_pending()
        now = datetime.now().astimezone()  # timezone-aware
        delivered_any = False

        for capsule in pending:
            if now >= capsule.scheduled_time and not capsule.is_delivered:
                print(f"Delivering to user {capsule.creator_id}: {capsule.message}")
                capsule.mark_delivered()
                self.repository.update(capsule)
                delivered_any = True
        
        if not pending:
            print("No pending capsules to deliver.")
        elif not delivered_any:
            pass 
