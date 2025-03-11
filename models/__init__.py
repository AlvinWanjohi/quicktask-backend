from flask_sqlalchemy import SQLAlchemy

# Initialize the database
db = SQLAlchemy()

# Import models to be recognized when creating tables
from .user import User
from .task import Task
from .bid import Bid
