from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import User, Hobby, Daily
from . import db
import requests

views = Blueprint("views", __name__)

def _to_int(string:str) -> int :
    """
    string:str -> takes in a given string and tries to convert it into an integer, if not, returns 0
    """
    try:
        string = int(string)
    except Exception:
        string = 0
    return string

##############################################################
## FLASK VIEWS
##############################################################

@views.route("/")
@views.route("/home")
def home():
    """
    Main homepage of the website
    """
    url = "https://zenquotes.io/api/random"
    response = requests.get(url)
    a = response.json()[0]
    return render_template("home.html", current_user=current_user, quote=a["q"], author=["a"])

@views.route("/create-hobby/<username>", methods=["POST"])
@login_required
def create_hobby(username):
    """
    Creates the hobby
    """
    user = User.query.filter_by(username=username).first()
    text = request.form.get('text')
    price = request.form.get('price')
    if current_user.permission_level < 3 and current_user.username != username:
        flash("You cannot create a hobby for someone else!", category="error")
        return redirect(url_for("views.dashboard", username=current_user.username))
    elif not text:
        flash("Text field cannot be empty!", category="error")
    elif not user:
        flash("User doesn't exist!", category="error")
    elif not price:
        flash("Price field cannot be empty!", category="error")
    elif _to_int(price) > 5:
        flash("Price field for hobbies cannot be more than 5!", category="error")
    elif len(text) > 50:
        flash("Text is too long!", category="error")
    else:
        hobby = Hobby(text=text, price=_to_int(price), author=user.id)
        db.session.add(hobby)
        db.session.commit()
        flash("Hobby task created!", category="success")

    return redirect(url_for("views.dashboard", username=user.username))

@views.route("/delete-hobby/<id>", methods=["POST"])
@login_required
def delete_hobby(id):
    """
    Deletes a given hobby using the specified <id>
    """
    hobby = Hobby.query.filter_by(id=id).first()
    user = hobby.user
    
    if not hobby:
        flash("Cannot delete, non-existant hobby!", category="error")
    elif current_user.permission_level < 3 and current_user.id != user.id:
        flash("You do not have permission to delete this hobby!", category="error")
        return redirect(url_for("views.dashboard", username=current_user.username))
    else:
        db.session.delete(hobby)
        db.session.commit()
        flash("Hobby has been deleted successfully!", category="success")
    
    return redirect(url_for("views.dashboard", username=user.username))

@views.route("/create-daily/<username>", methods=["POST"])
@login_required
def create_daily(username):
    user = User.query.filter_by(username=username).first()
    text = request.form.get('text')
    price = request.form.get('price')

    if current_user.permission_level < 3 and current_user.username != username:
        flash("You cannot create a hobby for someone else!", category="error")
        return redirect(url_for("views.dashboard", username=current_user.username))
    elif not text:
        flash("Text field cannot be empty!", category="error")
    elif not user:
        flash("User doesn't exist!", category="error")
    elif not price:
        flash("Price field cannot be empty!", category="error")
    elif _to_int(price) > 10:
        flash("Price field for hobbies cannot be more than 10!", category="error")
    elif len(text) > 50:
        flash("Text is too long!", category="error")
    else:
        daily = Daily(text=text, price=_to_int(price), author=user.id)
        db.session.add(daily)
        db.session.commit()
        flash("Daily task created!", category="success")

    return redirect(url_for("views.dashboard", username=user.username))

@views.route("/delete-daily/<id>/", methods=["POST"])
@login_required
def delete_daily(id):
    daily = Daily.query.filter_by(id=id).first()
    user = daily.user
    if not daily:
        flash("Cannot delete, non-existant daily task!", category="error")
    elif current_user.permission_level < 3 and current_user.id != user.id:
        flash("You do not have permission to delete this hobby!", category="error")
        return redirect(url_for("views.dashboard", username=current_user.username))
    elif not user:
        flash("User doesn't exist!", category="error")
    elif current_user.id != daily.user.id:
        flash("You do not have permission to delete this daily task!", category="error")
    else:
        db.session.delete(daily)
        db.session.commit()
        flash("Daily task has been deleted successfully!", category="success")
    
    return redirect(url_for("views.dashboard", username=user.username))


@views.route("/dashboard/<username>")
@login_required
def dashboard(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash("No user with that username exists!", category="error")
        return redirect(url_for("views.home"))
    elif current_user.permission_level < 2 and current_user.id != user.id:
        flash("You can't view other's dashboard!", category="error")
        return redirect(url_for("views.home"))

    return render_template("dashboard.html", current_user=current_user, hobbies=user.hobbies, dailies=user.dailies, tickets=user.tickets)

@views.route("/toggle-daily/<id>", methods=["POST"])
@login_required
def toggle_daily(id):
    daily = Daily.query.filter_by(id=id).first()

    if not daily:
        flash("Cannot find specified daily task!", category="error")
        return redirect(url_for("views.dashboard", username=current_user.username))

    user = daily.user

    if current_user.permission_level < 3 and current_user.id != user.id:
        flash("You do not have permission to change others daily!", category="error")
        return redirect(url_for("views.dashboard", username=current_user.username))
    elif daily.checked:
        flash(f"Unchecked {daily.text}!", category="success")
        user.tickets -= daily.price
        flash(f"Lost {daily.price} tickets!", category="error")
    elif not daily.checked:
        flash(f"Checked {daily.text}!", category="success")
        user.tickets += daily.price
        flash(f"Gained {daily.price} tickets!", category="success")
    else:
        daily.checked = not daily.checked
        db.session.commit()

    return redirect(url_for("views.dashboard", username=user.username))

@views.route("/toggle-hobby/<id>", methods=["POST"])
@login_required
def toggle_hobby(id):
    hobby = Hobby.query.filter_by(id=id).first()

    if not hobby:
        flash("Cannot find specified hobby task!", category="error")
        return redirect(url_for("views.dashboard", username=current_user.username))

    user = hobby.user

    if current_user.permission_level < 3 and current_user.id != user.id:
        flash("You do not have permission to change others hobby!", category="error")
        return redirect(url_for("views.dashboard", username=current_user.username))
    elif hobby.checked:
        flash(f"Unchecked {hobby.text}!", category="success")
        user.tickets -= hobby.price
        flash(f"Lost {hobby.price} tickets!", category="error")
    elif not hobby.checked:
        flash(f"Checked {hobby.text}!", category="success")
        user.tickets += hobby.price
        flash(f"Gained {hobby.price} tickets!", category="success")
    else:
        hobby.checked = not hobby.checked
        db.session.commit()

    return redirect(url_for("views.dashboard", username=user.username))
    