from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    tickets = db.Column(db.Integer, nullable=False, default=0)
    habits = db.relationship("Habit", backref='user', passive_deletes=True)

class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    text = db.Column(db.String(50), unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False, default=0)
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)

class Daily(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    text = db.Column(db.String(50), unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False, default=0)
    checked = db.Column(db.Boolean, nullable=False, default=False)
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)

