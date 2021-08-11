from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    permission_level = db.Column(db.Integer, nullable=False, default=0)
    """
    permission level : 
    0 - default member -> make posts/comments, delete own posts/comments
    1 - healthcare -> same as above + have a verified badge next to name.
    2 - admin - > same as 0 + have admin badge next to name. Can delete any post, comments, can verify other users as healthcare
    """
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    tickets = db.Column(db.Integer, nullable=False, default=0)
    hobbies = db.relationship("Hobby", backref='user', passive_deletes=True)
    dailies = db.relationship("Daily", backref='user', passive_deletes=True)
    posts = db.relationship("Post", backref='user', passive_deletes=True)
    comments = db.relationship("Comment", backref='user', passive_deletes=True)

class Hobby(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    text = db.Column(db.String(50), unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False, default=3)
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    checked = db.Column(db.Boolean, nullable=False, default=False)

class Daily(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    text = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer, nullable=False, default=8)
    checked = db.Column(db.Boolean, nullable=False, default=False)
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    text = db.Column(db.String(50), nullable=False)
    severity = db.Column(db.Boolean, nullable=False, default=False)
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    comments = db.relationship("Comment", backref='post', passive_deletes=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    text = db.Column(db.String(50), nullable=False)
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete="CASCADE"), nullable=False)

