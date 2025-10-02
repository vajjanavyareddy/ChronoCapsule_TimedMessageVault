from supabase import create_client, Client
from model.user import User

class UserRepository:
    def __init__(self, url, key):
        self.supabase: Client = create_client(url, key)

    def save(self, user: User):
        self.supabase.table("users").insert({
            
            "name": user.name,
            "email": user.email
        }).execute()

    def find_by_id(self, user_id):
        data = self.supabase.table("users").select("*").eq("id", user_id).execute()
        if data.data:
            u = data.data[0]
            return User(u["id"], u["name"], u["email"])
        return None

    def find_all(self):
        data = self.supabase.table("users").select("*").execute()
        users = []
        for u in data.data:
            users.append(User(u["id"], u["name"], u["email"]))
        return users
