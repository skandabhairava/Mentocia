from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import User, Habit, Daily
from . import db

views = Blueprint("views", __name__)

@views.route("/")
@views.route("/home")
@login_required
def home():
    return render_template("home.html", user=current_user)

@views.route("/create-post", methods=["POST"])
@login_required
def create_post():

    if request.method == "POST":
        title = request.form.get('title')
        text = request.form.get('text')
        if not text:
            flash("Post cannot be empty!", category="error")
        elif not title:
            flash("Title cannot be empty!", category="error")
        elif len(text) > 200 or len(title) > 50:
            flash("Title/Post is too long!", category="error")
        else:
            post = Post(text=text, title=title, author=current_user.id)
            db.session.add(post)
            db.session.commit()
            flash("Post created!", category="success")
            return redirect(url_for("views.home"))

    return render_template('create_post.html', user=current_user)

@views.route("/delete-post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash("Post does not exist!", category="error")
    elif current_user.id != post.user.id:
        flash("You do not have permission to delete this post!", category="error")
    else:
        db.session.delete(post)
        db.session.commit()
        flash("Post has been deleted successfully!", category="success")
    
    return redirect(url_for("views.home"))

@views.route("/user/<username>/posts")
@login_required
def posts(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash("No user with that username exists!", category="error")
        return redirect(url_for("views.home"))

    posts = user.posts[::-1]
    return render_template("posts.html", user=current_user, posts=posts, username=username)

@views.route("/post/<id>")
@login_required
def view_single_post(id):
    post = Post.query.filter_by(id=id).first()

    if not post:
        flash("No such Post exists", category="error")
        return redirect(url_for("views.home"))

    return render_template("single_post.html", post=post, user=current_user)

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
    elif current_user.id != comment.author:
        flash("You do not have permission to delete this comment!", category="error")
    else:
        url_redirect = url_for("views.view_single_post", id=comment.post.id)
        db.session.delete(comment)
        db.session.commit()
        flash("Comment has been deleted successfully!", category="success")
    
    return redirect(url_redirect)

@views.route("/user/<username>")
@login_required
def view_user(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        flash("User doesn't exist", category="error")
        return redirect(url_for("views.home"))
    
    return render_template('user_profile.html', user=current_user, account=user)
    