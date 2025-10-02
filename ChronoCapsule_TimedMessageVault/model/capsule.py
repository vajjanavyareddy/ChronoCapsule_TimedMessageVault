from datetime import datetime

class Capsule:
    def __init__(self, id, title, message, creator_id, scheduled_time, is_delivered=False):
        self.id = id
        self.title = title
        self.message = message
        self.creator_id = creator_id
        self.scheduled_time = scheduled_time
        self.is_delivered = is_delivered

    def mark_delivered(self):
        self.is_delivered = True
