from utils.database import db

class Bid(db.Model):
    __tablename__ = "bids"

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    freelancer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)

    def __init__(self, amount, freelancer_id, task_id):
        self.amount = amount
        self.freelancer_id = freelancer_id
        self.task_id = task_id

    def to_dict(self):
        """Return bid details as a dictionary."""
        return {
            "id": self.id,
            "amount": self.amount,
            "freelancer_id": self.freelancer_id,
            "task_id": self.task_id,
        }
