from flask import Blueprint, render_template, redirect, url_for, request, flash
from sqlalchemy.sql.functions import user
from . import db
from .models import User, Daily
import re
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                flash("Logged in successfully!", category="success")
                return redirect(url_for("views.dashboard", username=user.username))
            else:
                flash("Password is incorrect!", category="error")
        else:
            flash("Email does not exist!", category="error")

    return render_template("login.html", user=current_user)

def _checkstring(string:str, invalid_characters):
    """
    Returns true if one character in inputted string matches invalid characters
    """
    #invalid_characters = ";:'\".,\\/ "
    for i in string:
        if i in invalid_characters:
            return True
    return False

def _validate_username(username:str):
    """
    Return true if theres an error in validating username
    Return false if theres no error in validating username
    """
    if len(username) > 50:
        return True
    elif username.startswith("_") or username.endswith("_"):
        return True
    elif _checkstring(username, ";:'\".,\\/ "):
        return True

    return False
    

@auth.route("/sign-up", methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        email_exists = User.query.filter_by(email=email).first()
        user_exists = User.query.filter_by(username=username).first()
        if email_exists:
            flash('Email is already in use', category='error')
        elif user_exists:
            flash('Username is already in use', category='error')
        elif password1 != password2:
            flash('Password don\'t match', category='error')
        elif len(username) < 2:
            flash('Username is too short', category='error')
        elif len(password1) < 6:
            flash('Password is too short', category='error')
        elif not (re.search("^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$",email)):  
            flash('Invalid Email', category="error")
        elif _validate_username(username):  
            flash('Invalid Username', category="error")
        else:  
            new_user = User(email=email, username=username.lower(), password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True) # ONLY USE IF U WANT TO LOGIN IMMEDIATELY AFTER SIGNING UP
            flash("User Account created!", category="success")
            get_user = User.query.filter_by(username=username).first()
            daily_1 = Daily(text="Get plenty of sleep", price=8, author=get_user.id)
            daily_2 = Daily(text="10 min of exercise", price=8, author=get_user.id)
            daily_3 = Daily(text="3 liters of water", price=8, author=get_user.id)
            daily_4 = Daily(text="meditate for 2 min", price=8, author=get_user.id)
            daily_5 = Daily(text="eat healthy food", price=8, author=get_user.id)
            db.session.add(daily_1)
            db.session.add(daily_2)
            db.session.add(daily_3)
            db.session.add(daily_4)
            db.session.add(daily_5)
            db.session.commit()
            return redirect(url_for("views.dashboard", username=current_user.username))

    return render_template("signup.html", user=current_user)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Successfully logged out!", category="success")
    return redirect(url_for("views.home"))

