from utils.database import db
from models.bid import Bid
from flask import jsonify

class BidService:
    """Service layer for managing bids."""

    @staticmethod
    def place_bid(data): 
        """Places a new bid with error handling and validation."""
        required_fields = ["task_id", "freelancer_id", "amount"]

        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        try:
            task_id = int(data["task_id"])
            freelancer_id = int(data["freelancer_id"])
            amount = float(data["amount"])

            
            if amount <= 0:
                return jsonify({"error": "Bid amount must be a positive number"}), 400

            
            new_bid = Bid(task_id=task_id, freelancer_id=freelancer_id, amount=amount)
            db.session.add(new_bid)
            db.session.commit()

            return jsonify({
                "message": "Bid placed successfully",
                "bid": {
                    "id": new_bid.id,
                    "task_id": new_bid.task_id,
                    "freelancer_id": new_bid.freelancer_id,
                    "amount": new_bid.amount,
                    "created_at": new_bid.created_at.strftime('%Y-%m-%d %H:%M:%S')
                }
            }), 201

        except ValueError:
            return jsonify({"error": "Invalid data type: task_id and freelancer_id must be integers, amount must be a number"}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Database error", "details": str(e)}), 500
