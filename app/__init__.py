from flask import Flask, send_from_directory, render_template, request
from flask_migrate import Migrate, upgrade
from sqlalchemy import inspect
from .config import config_by_name
from .models import db, User
from .endpoints import payment_blueprint


def create_app(config_name):
    app = Flask(__name__, template_folder='../templates')
    app.config.from_object(config_by_name[config_name])

    db.init_app(app)
    migrate = Migrate(app, db)

    app.register_blueprint(payment_blueprint, url_prefix='/v1')  # Register blueprint with prefix '/v1'

    with app.app_context():
        inspector = inspect(db.engine)
        # Check if the database exists, and create it along with the tables if it doesn't
        if not inspector.get_table_names():
            db.create_all()
            User.create_test_user()  # Create test user and card

    return app
