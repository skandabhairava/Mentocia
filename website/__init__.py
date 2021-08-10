from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash
import datetime

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

    from .models import User, Daily, Hobby

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
    admin.add_view(MyModelView(Hobby, db.session))

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    def resettt():
        reset_daily(app)

    from apscheduler.schedulers.background import BackgroundScheduler

    today = datetime.datetime.now()
    start_time = datetime.datetime(year=today.year, month=today.month, day=today.day, hour=23, minute=59, second=0)
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=resettt, trigger="interval", hours=24, start_date=start_time)
    scheduler.start()

    return app

def create_database(app):
    if not path.exists("website/" + DB_NAME):
        from .models import User
        db.create_all(app=app)
        print("Created database")

def reset_daily(app):
    print("removing all checked items")
    with app.app_context():
        from .models import Daily, Hobby
        dailies = Daily.query.all()
        hobbies = Hobby.query.all()

        for daily in dailies:
            if daily.checked == True:
                #print("Daily was actually checked\n\n\n")
                daily.checked = False
            db.session.commit()

        for hobby in hobbies:
            if hobby.checked == True:
                #print("Hobby was actually checked\n\n\n")
                hobby.checked = False
            db.session.commit()

    print("Done removing all checked items")
