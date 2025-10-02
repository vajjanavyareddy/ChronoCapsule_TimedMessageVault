# repository/capsule_repository.py
from datetime import datetime, timezone
from supabase import create_client, Client
from model.capsule import Capsule

class CapsuleRepository:
    def __init__(self, url, key):
        self.supabase: Client = create_client(url, key)

    def save(self, capsule: Capsule):
        self.supabase.table("capsules").insert({
            
            "title": capsule.title,
            "message": capsule.message,
            "creator_id": capsule.creator_id,
            "scheduled_time": capsule.scheduled_time.isoformat(),
            "is_delivered": capsule.is_delivered
        }).execute()

    def find_all_pending(self):
        data = self.supabase.table("capsules").select("*").eq("is_delivered", False).execute()
        capsules = []
        for c in data.data:
            
            utc_time = datetime.fromisoformat(c["scheduled_time"])
            local_time = utc_time.astimezone() 
            capsules.append(Capsule(
                c["id"], c["title"], c["message"], c["creator_id"],
                local_time,
                c["is_delivered"]
            ))
        return capsules

    def update(self, capsule: Capsule):
        self.supabase.table("capsules").update({
            "is_delivered": capsule.is_delivered
        }).eq("id", capsule.id).execute()
