from flask import Blueprint, request, jsonify
from services.bid_service import BidService

bid_bp = Blueprint("bid", __name__)

@bid_bp.route("/", methods=["POST"])
def bid_on_task():
    """Handles placing a bid on a task."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid request, no data provided"}), 400

        required_fields = ["amount", "freelancer_id", "task_id"]
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        
        response = BidService.place_bid(data)

        return response, 201 

    except Exception as e:
        return jsonify({"error": "An error occurred while placing the bid", "details": str(e)}), 500
