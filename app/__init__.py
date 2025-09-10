from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()
login_manager = LoginManager()


def create_app(config_class="config.Config") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = "main.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    from . import models  # noqa: F401  # Ensure models are registered
    from .routes import main

    app.register_blueprint(main)


    @app.template_filter("formatdate")
    def format_date(value, format="%B %d, %Y"):
        return value.strftime(format)

    with app.app_context():
        db.create_all()

    return app
