from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy import inspect

from .config import Config
from .endpoints import payment_blueprint
from .models import db, User


def create_app():
    app = Flask(__name__, template_folder='../templates')
    app.config.from_object(Config())

    db.init_app(app)
    migrate = Migrate(app, db)

    app.register_blueprint(payment_blueprint, url_prefix='/v1')  # Register blueprint with prefix '/v1'

    with app.app_context():
        inspector = inspect(db.engine)
        # Check if the database exists, and create it along with the tables if it doesn't
        if not inspector.get_table_names():
            db.create_all()
            User.create_test_user()  # Create test user and card

    # Enable CORS
    CORS(app)

    return app
