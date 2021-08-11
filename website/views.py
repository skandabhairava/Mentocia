from operator import not_
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import User, Hobby, Daily, Post, Comment
from sqlalchemy import not_
from . import db
from sqlalchemy.orm.attributes import flag_modified
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

def _to_bool(string:str) -> bool :
    """
    string:str -> takes in a given string and tries to convert it into a boolean, if not, returns False
    """
    try:
        return string.lower() in ("true", "yes", "t", "1")
    except Exception:
        return False

##############################################################
## FLASK VIEWS FOR DASHBOARD
##############################################################

@views.route("/")
@views.route("/home")
def home():
    """
    Main homepage of the website
    """
    return render_template("home.html", current_user=current_user)

@views.route("/create-hobby/<username>", methods=["POST"])
@login_required
def create_hobby(username):
    """
    Creates the hobby
    """
    user = User.query.filter_by(username=username).first()
    text = request.form.get('text')
    price = "3"
    if current_user.permission_level < 2 and current_user.username != username:
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

@views.route("/delete-hobby/<id>")
@login_required
def delete_hobby(id):
    """
    Deletes a given hobby using the specified <id>
    """
    hobby = Hobby.query.filter_by(id=id).first()
    user = hobby.user
    
    if not hobby:
        flash("Cannot delete, non-existant hobby!", category="error")
    elif current_user.permission_level < 2 and current_user.id != user.id:
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
    price = "8"

    if current_user.permission_level < 2 and current_user.username != username:
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

@views.route("/delete-daily/<id>/")
@login_required
def delete_daily(id):
    daily = Daily.query.filter_by(id=id).first()
    user = daily.user
    if not daily:
        flash("Cannot delete, non-existant daily task!", category="error")
    elif current_user.permission_level < 2 and current_user.id != user.id:
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

@views.route("/dashboard")
@login_required
def dashboard_main():
    return redirect(url_for("views.dashboard", username=current_user.username))

@views.route("/dashboard/<username>")
@login_required
def dashboard(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash("No user with that username exists!", category="error")
        return redirect(url_for("views.home"))
    elif current_user.permission_level < 1 and current_user.id != user.id:
        flash("You can't view other's dashboard!", category="error")
        return redirect(url_for("views.dashboard", username=current_user.username))
    
    url = "https://zenquotes.io/api/random"
    response = requests.get(url)
    a = response.json()[0]
    posts = user.posts[::-1]

    return render_template("dashboard.html", current_user=current_user, user=user, hobbies=user.hobbies, dailies=user.dailies, tickets=user.tickets, quote=a["q"], author=a["a"], posts=posts)

@views.route("/posts/<username>")
@login_required
def user_posts(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash("No user with that username exists!", category="error")
        return redirect(url_for("views.home"))
    elif current_user.permission_level < 1 and current_user.id != user.id:
        flash("You can't view other's posts!", category="error")
        return redirect(url_for("views.dashboard", username=current_user.username))
    
    posts = user.posts[::-1]

    return render_template("post_div.html", current_user=current_user, posts=posts)

@views.route("/toggle-daily/<id>")
@login_required
def toggle_daily(id):
    daily = Daily.query.filter_by(id=id).first()

    if not daily:
        flash("Cannot find specified daily task!", category="error")
        return redirect(url_for("views.dashboard", username=current_user.username))

    user = User.query.filter_by(id=daily.author).first()

    if current_user.permission_level < 2 and current_user.id != user.id:
        flash("You do not have permission to change others daily!", category="error")
        return redirect(url_for("views.dashboard", username=current_user.username))
    elif daily.checked:
        flash(f"Unchecked {daily.text}!", category="success")
        user.tickets -= daily.price
        daily.checked = not daily.checked
        db.session.commit()
        flash(f"Lost {daily.price} tickets!", category="error")
    elif not daily.checked:
        flash(f"Checked {daily.text}!", category="success")
        user.tickets += daily.price
        daily.checked = not daily.checked
        db.session.commit()
        flash(f"Gained {daily.price} tickets!", category="success")
    else:
        print("I dont know how you got here")

    return redirect(url_for("views.dashboard", username=user.username))

@views.route("/toggle-hobby/<id>")
@login_required
def toggle_hobby(id):
    hobby = Hobby.query.filter_by(id=id).first()

    if not hobby:
        flash("Cannot find specified hobby task!", category="error")
        return redirect(url_for("views.dashboard", username=current_user.username))

    user = User.query.filter_by(id=hobby.author).first()

    if current_user.permission_level < 2 and current_user.id != user.id:
        flash("You do not have permission to change others hobby!", category="error")
        return redirect(url_for("views.dashboard", username=current_user.username))
    elif hobby.checked:
        flash(f"Unchecked {hobby.text}!", category="success")
        user.tickets -= hobby.price
        hobby.checked = not hobby.checked
        db.session.commit()
        flash(f"Lost {hobby.price} tickets!", category="error")
    elif not hobby.checked:
        flash(f"Checked {hobby.text}!", category="success")
        user.tickets += hobby.price
        hobby.checked = not hobby.checked
        db.session.commit()
        flash(f"Gained {hobby.price} tickets!", category="success")
    else:
        print("I dont know how you got here")

    return redirect(url_for("views.dashboard", username=user.username))

@views.route("/redeem-8/<username>")
@login_required
def redeem_8(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash("user doesn't exist", category="error")
        return redirect(url_for("views.dashboard", username=current_user.username))
    if current_user.permission_level < 2 and current_user.id != user.id:
        flash("You do not have permission to change others hobby!", category="error")
        return redirect(url_for("views.dashboard", username=current_user.username))
    if user.tickets < 8:
        flash("You have less than 8 tickets in your account!", category="error")
    else:
        user.tickets -= 8
        db.session.commit()
        flash("Good job!!\nTreat yourself by having a chocolate!", category="success")

    return redirect(url_for("views.dashboard", username=user.username))

@views.route("/redeem-20/<username>")
@login_required
def redeem_20(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash("user doesn't exist", category="error")
        return redirect(url_for("views.dashboard", username=current_user.username))
    if current_user.permission_level < 2 and current_user.id != user.id:
        flash("You do not have permission to change others hobby!", category="error")
        return redirect(url_for("views.dashboard", username=current_user.username))
    if user.tickets < 20:
        flash("You have less than 20 tickets in your account!", category="error")
    else:
        user.tickets -= 20
        db.session.commit()
        flash("Good job!!\nTreat yourself by taking a 2hr break!", category="success")

    return redirect(url_for("views.dashboard", username=user.username))

##############################################################
## FLASK VIEWS FOR FORUM
##############################################################

@views.route("/forum")
@login_required
def forum():
    if current_user.permission_level != 1:
        posts = Post.query.filter(Post.severity != True).all()[::-1]
    else:
        posts = Post.query.all()[::-1]
    return render_template("post_div.html", current_user=current_user, posts=posts)

@views.route("/create-post", methods=["GET", "POST"])
@login_required
def create_post():
    if request.method == "POST":
        text = request.form.get('text')
        severity = request.form.get('range')
        if not text:
            flash("Post cannot be empty!", category="error")
        elif not severity:
            flash("Severity value cannot be empty!", category="error")
        elif len(text) > 200:
            flash("Title/Post is too long!", category="error")
        else:
            post = Post(text=text, severity=_to_bool(severity), author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash("Post created!", category="success")
            return redirect(url_for("views.forum"))

    return render_template('create_post.html', current_user=current_user)

@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash("Post does not exist!", category="error")
    elif current_user.permission_level < 1 and current_user.id != post.user.id:
        flash("You can't delete others posts!", category="error")
        return redirect(url_for("views.forum"))
    else:
        db.session.delete(post)
        db.session.commit()
        flash("Post has been deleted successfully!", category="success")
    
    return redirect(url_for("views.forum"))

@views.route("/create-comment/<id>", methods=['POST'])
@login_required
def create_comment(id):
    post = Post.query.filter_by(id=id).first()
    text = request.form.get('text')
    if not post:
        flash("No such Post exists", category="error")
    elif not text:
        flash("Comment cannot be empty", category="error")
    else:
        comment = Comment(text=text, author=current_user.id, post_id=id)
        db.session.add(comment)
        db.session.commit()
        flash("Comment has been posted!", category="success")

    return redirect(url_for("views.view_single_post", id=id))

@views.route("/delete-comment/<id>")
@login_required
def delete_comment(id):
    comment = Comment.query.filter_by(id=id).first()

    if not comment:
        flash("Comment does not exist!", category="error")
    elif current_user.permission_level < 1 and current_user.id != comment.user.id:
        flash("You can't delete others comments!", category="error")
    else:
        url_redirect = url_for("views.view_single_post", id=comment.post.id)
        db.session.delete(comment)
        db.session.commit()
        flash("Comment has been deleted successfully!", category="success")
    
    return redirect(url_redirect)

@views.route("/post/<id>")
@login_required
def view_single_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash("No such Post exists", category="error")
        return redirect(url_for("views.forum"))

    return render_template("single_post.html", post=post, current_user=current_user)