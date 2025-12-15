import os

from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

from core.configuration.configuration import get_app_version
from core.managers.config_manager import ConfigManager
from core.managers.error_handler_manager import ErrorHandlerManager
from core.managers.logging_manager import LoggingManager
from core.managers.module_manager import ModuleManager

# Load environment variables
load_dotenv()

# Create the instances
db = SQLAlchemy()
migrate = Migrate()
sess = Session()


def create_app(config_name="development"):
    app = Flask(__name__)

    # Load configuration according to environment
    config_manager = ConfigManager(app)
    config_manager.load_config(config_name=config_name)

    # Initialize SQLAlchemy and Migrate with the app
    db.init_app(app)
    migrate.init_app(app, db)

    # Initilize Session
    app.config["SESSION_SQLALCHEMY"] = db
    from flask_session.sqlalchemy import sqlalchemy as flask_session_module

    def patched_create_session_model(db, table_name, *args, **kwargs):
        """Patched version that adds extend_existing=True to avoid table redefinition errors"""

        class Session(db.Model):
            __tablename__ = table_name
            __table_args__ = {"extend_existing": True}

            id = db.Column(db.Integer, primary_key=True)
            session_id = db.Column(db.String(255), unique=True, nullable=False)
            data = db.Column(db.LargeBinary, nullable=False)
            expiry = db.Column(db.DateTime, nullable=False)

        return Session

    flask_session_module.create_session_model = patched_create_session_model

    sess.init_app(app)

    # Register modules
    module_manager = ModuleManager(app)
    module_manager.register_modules()

    # Register login manager
    from flask_login import LoginManager

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    @login_manager.user_loader
    def load_user(user_id):
        from app.modules.auth.models import User

        return User.query.get(int(user_id))

    # Set up logging
    logging_manager = LoggingManager(app)
    logging_manager.setup_logging()

    # Initialize error handler manager
    error_handler_manager = ErrorHandlerManager(app)
    error_handler_manager.register_error_handlers()

    from app.modules.auth.middleware.session_tracker import setup_session_tracking

    setup_session_tracking(app)

    # Injecting environment variables into jinja context
    @app.context_processor
    def inject_vars_into_jinja():
        return {
            "FLASK_APP_NAME": os.getenv("FLASK_APP_NAME"),
            "FLASK_ENV": os.getenv("FLASK_ENV"),
            "DOMAIN": os.getenv("DOMAIN", "localhost"),
            "APP_VERSION": get_app_version(),
        }

    return app


if __name__ == "__main__":
    app = create_app()
