from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm

app = Flask(__name__)

app.config["SECRET_KEY"] = "31ae41c06b443067a21ed022c9736d29"

posts = [
    {
        "author": "Sebastian Hoppe",
        "title": "Blog Post 1",
        "content": "First Post Content",
        "date_posted": "September 04, 2025"
    },
    {
        "author": "Luisa Harmening",
        "title": "Blog Post 2",
        "content": "Second Post Content",
        "date_posted": "September 04, 2025"
    },
]

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", posts=posts)

@app.route("/about")
def about():
    return render_template("about.html", title="About")

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f"Account created for {form.username.data}!", "success")
        return redirect(url_for("home"))
    return render_template("register.html", title="Register", form=form)

if __name__ == "__main__":
    app.run(debug=True)