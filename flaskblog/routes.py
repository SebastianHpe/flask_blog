import os
import secrets

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from flask_mail import Message
from PIL import Image
from sqlalchemy import select

from flaskblog import db, mail
from flaskblog.forms import (
    LoginForm,
    PostForm,
    RegistrationForm,
    RequestResetForm,
    ResetPasswordForm,
    UpdateAccountForm,
)
from .models import Post, User

main = Blueprint("main", __name__)


@main.route("/")
@main.route("/home")
def home():
    page = request.args.get("page", default=1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template("home.html", title="Home", posts=posts)


@main.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data.lower())
        user.password = form.password.data  # the setter hashes the password

        db.session.add(user)
        db.session.commit()
        flash("Your account has been created! You are now able to log in!", "success")
        return redirect(url_for("main.login"))
    return render_template("register.html", title="Register", form=form)


@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = LoginForm()
    if form.validate_on_submit():
        stmt = select(User).filter_by(email=form.email.data.lower())
        user = db.session.execute(stmt).scalar_one_or_none()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("main.home"))
        else:
            flash("Login unsuccessful. Please check email and password.", "danger")
    return render_template("login.html", title="Login", form=form)


@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.home"))


@main.route("/about")
def about():
    return render_template("about.html", title="About")


@main.route("/post/new", methods=["POST", "GET"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data, content=form.content.data, author=current_user
        )
        db.session.add(post)
        db.session.commit()
        flash("Post has been created", "success")
        return redirect(url_for("main.home"))
    return render_template("create_post.html", title="New Post", form=form)


@main.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", title=post.title, post=post)


@main.route("/post/<int:post_id>/update", methods=["POST", "GET"])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data

        db.session.commit()
        flash("Post has been updated", "success")
        return redirect(url_for("main.post", post_id=post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
    return render_template("create_post.html", title="Update Post", form=form)


@main.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Post has been deleted", "success")
    return redirect(url_for("main.home", post_id=post.id))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_filename = random_hex + f_ext
    picture_path = os.path.join(
        current_app.root_path, "static/profile_pics", picture_filename
    )
    output_size = (125, 125)
    resized_image = Image.open(form_picture)
    resized_image.thumbnail(output_size)

    resized_image.save(picture_path)

    return picture_filename


@main.route("/account", methods=["POST", "GET"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data.lower()
        db.session.commit()
        flash("Your account has been updated!", "success")
        return redirect(url_for("main.account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for("static", filename="profile_pics/" + current_user.image_file)
    return render_template(
        "account.html", title="Account", image_file=image_file, form=form
    )


@main.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get("page", default=1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template("user_posts.html", title="Home", posts=posts, user=user)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message(
        "Password Reset Request", sender="noreply@demo.com", recipients=[user.email]
    )
    msg.body = f"""To reset your password, visit the following link:
{url_for("main.reset_token", token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
"""
    mail.send(msg)


@main.route("/reset_password", methods=["POST", "GET"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = db.session.execute(
            db.select(User).filter_by(email=form.email.data.lower())
        ).scalar_one_or_none()
        send_reset_email(user)
        flash(
            "An email has been sent with instructions to reset your password.", "info"
        )
        return redirect(url_for("main.login"))
    return render_template("reset_request.html", title="Reset Password", form=form)


@main.route("/reset_password/<token>", methods=["POST", "GET"])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    user = User.verify_reset_token(token)
    if not user:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("main.reset_request"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = form.password.data  # the setter hashes the password
        db.session.commit()
        flash("Your password has been updated!", "success")
        return redirect(url_for("main.login"))
    return render_template("reset_token.html", title="Reset Password", form=form)
