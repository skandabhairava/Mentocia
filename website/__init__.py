from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "sambarodne"
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_NAME}"
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from .models import User, Daily, Habit

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    class MyModelView(ModelView):
        def is_accessible(self):
            return current_user.permission_level == 3

    admin = Admin(app)
    admin.add_view(MyModelView(User, db.session))
    admin.add_view(MyModelView(Daily, db.session))
    admin.add_view(MyModelView(Habit, db.session))

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

def create_database(app):
    if not path.exists("website/" + DB_NAME):
        from .models import User
        db.create_all(app=app)
        print("Created database")