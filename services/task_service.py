from flask import jsonify, request
from utils.database import db
from models.task import Task

class TaskService:
    """Service layer for task operations."""

    @staticmethod
    def create_task(data):
        """Creates a new task with validation and error handling."""
        required_fields = ["title", "description", "budget", "client_id"]

        
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        try:
            
            title = str(data["title"]).strip()
            description = str(data["description"]).strip()
            budget = float(data["budget"])
            client_id = int(data["client_id"])

            
            if not title or not description:
                return jsonify({"error": "Title and description cannot be empty"}), 400

        
            if budget <= 0:
                return jsonify({"error": "Budget must be greater than zero"}), 400

            
            new_task = Task(title=title, description=description, budget=budget, client_id=client_id)
            db.session.add(new_task)
            db.session.commit()

            return jsonify({"message": "Task posted successfully", "task_id": new_task.id}), 201

        except ValueError:
            return jsonify({"error": "Invalid data type for budget or client_id"}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Database error", "details": str(e)}), 500

    @staticmethod
    def get_tasks():
        """Retrieves tasks with optional pagination."""
        try:
            try:
                page = int(request.args.get("page", 1))
                per_page = int(request.args.get("per_page", 10))
            except ValueError:
                return jsonify({"error": "Invalid page or per_page parameter"}), 400

            tasks_paginated = Task.query.paginate(page=page, per_page=per_page, error_out=False)
            tasks = tasks_paginated.items

            return jsonify({
                "tasks": [
                    {"id": t.id, "title": t.title, "description": t.description, "budget": t.budget, "client_id": t.client_id}
                    for t in tasks
                ],
                "total": tasks_paginated.total,
                "pages": tasks_paginated.pages,
                "current_page": tasks_paginated.page
            }), 200

        except Exception as e:
            return jsonify({"error": "Failed to retrieve tasks", "details": str(e)}), 500

    @staticmethod
    def get_task_by_id(task_id):
        """Retrieves a single task by its ID."""
        try:
            try:
                task_id = int(task_id)
            except ValueError:
                return jsonify({"error": "Invalid task ID"}), 400

            task = Task.query.get(task_id)
            if not task:
                return jsonify({"error": "Task not found"}), 404

            return jsonify({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "budget": task.budget,
                "client_id": task.client_id
            }), 200

        except Exception as e:
            return jsonify({"error": "Failed to retrieve task", "details": str(e)}), 500
