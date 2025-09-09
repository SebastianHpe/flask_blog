from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_user, logout_user, current_user, login_required
from .forms import RegistrationForm, LoginForm
from . import db
from .models import User

main = Blueprint("main", __name__)


@main.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.password = form.password.data # the setter hashes the password

        db.session.add(user)
        db.session.commit()
        flash(f"Account created for {form.username.data}!", "success")
        return redirect(url_for("main.login"))
    return render_template("register.html", title="Register", form=form)


@main.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
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

@main.route("/")
@main.route("/home")
def home():
    return render_template("home.html", title="Home")

@main.route("/about")
def about():
    return render_template("about.html", title="About")

@main.route("/account")
@login_required
def account():
    return render_template("account.html", title="Account")