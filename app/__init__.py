from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def create_app(config_class="config.Config") -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    
    from . import models  # noqa: F401  # Ensure models are registered

    from .routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

    return app
