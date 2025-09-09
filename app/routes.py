from flask import Blueprint, render_template, url_for, flash, redirect
from .forms import RegistrationForm, LoginForm
from . import db
from .models import User

main = Blueprint("main", __name__)


@main.route("/register", methods=["GET", "POST"])
def register():
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
    form = LoginForm()
    if form.validate_on_submit():
        flash("You have been logged in!", "success")
        return redirect(url_for("main.register"))
    return render_template("login.html", title="Login", form=form)


@main.route("/")
@main.route("/home")
def home():
    return render_template("home.html", title="Home")

@main.route("/about")
def about():
    return render_template("about.html", title="About")