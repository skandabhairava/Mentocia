from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import User, Habit, Daily
from . import db

views = Blueprint("views", __name__)

@views.route("/")
@views.route("/home")
def home():
    return render_template("home.html")

@views.route("/create-habit", methods=["POST"])
@login_required
def create_habit():
    text = request.form.get('text')
    if not text:
        flash("Text field cannot be empty!", category="error")
    elif len(text) > 50:
        flash("Text is too long!", category="error")
    else:
        habit = Habit(text=text, author=current_user.id)
        db.session.add(habit)
        db.session.commit()
        flash("Habit created!", category="success")

    return redirect(url_for("views.dashboard", username=current_user.username))

@views.route("/delete-habit/<id>", methods=["POST"])
@login_required
def delete_habit(id):
    habit = Habit.query.filter_by(id=id).first()

    if not habit:
        flash("Cannot delete, non-existant habit!", category="error")
    elif current_user.id != habit.user.id:
        flash("You do not have permission to delete this habit!", category="error")
    else:
        db.session.delete(habit)
        db.session.commit()
        flash("Habit has been deleted successfully!", category="success")
    
    return redirect(url_for("views.dashboard", username=current_user.username))

@views.route("/dashboard/<username>")
@login_required
def dashboard(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash("No user with that username exists!", category="error")
        return redirect(url_for("views.home"))
    elif current_user.id != user.id:
        flash("You can't view other's dashboard!", category="error")
        return redirect(url_for("views.home"))

    habits = user.habits
    dailies = user.dailies

    return render_template("dashboard.html", user=current_user, habits=habits, dailies=dailies)
    