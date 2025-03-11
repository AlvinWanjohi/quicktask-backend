from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Task

task_bp = Blueprint("tasks", __name__)

@task_bp.route("/", methods=["GET"])
def get_tasks():
    """Retrieve all tasks from PostgreSQL."""
    tasks = Task.query.all()
    return jsonify([{
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "price": task.price
    } for task in tasks])

@task_bp.route("/", methods=["POST"])
@jwt_required()
def create_task():
    """Create a new task (authenticated)."""
    data = request.get_json()
    user_id = get_jwt_identity()

    new_task = Task(
        title=data["title"],
        description=data["description"],
        price=data["price"],
        user_id=user_id
    )

    db.session.add(new_task)
    db.session.commit()
    return jsonify({"message": "Task created successfully"}), 201
