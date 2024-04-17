from __future__ import annotations

import sys

from flask_bcrypt import Bcrypt
from flask import Flask, abort
from flask_mail import Mail

from main.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
import os

from datetime import date, datetime
from logger import StreamLogFormatter, FileLogFormatter

bcrypt = Bcrypt()
db = SQLAlchemy()
migrate = Migrate(compare_type=True)
logging.basicConfig(level=logging.DEBUG)
mail = Mail()

login_manager = LoginManager()
login_manager.login_view = "accounts.login"
login_manager.login_message_category = "warning"


def create_app(config_class=Config):
    # set up file paths for static resources
    app = Flask(
        __name__,
        static_url_path="/static",
        static_folder="web/static",
        template_folder="web/templates"
    )

    # set up environment variables
    app.config.from_object(config_class)

    # set up https / security
    # Talisman(
    #     app,
    #     content_security_policy=None
    # )

    # bcrypt
    bcrypt.init_app(app)

    # models
    from .modules.accounts import models
    from .modules.lists import models
    from .modules.chores import models
    from .modules.chore_logs import models
    from .modules.invitations import models

    # database
    db.app = app
    db.init_app(app)
    # looks like we don't need create_all() because we are doing migrations
    # with app.app_context():
    #     db.create_all()
    migrate.init_app(app, db)

    # routes and blueprints
    from .modules.main.routes import main
    from .modules.accounts.routes import accounts
    from .modules.errors.handlers import errors
    from .modules.lists.routes import lists
    from .modules.chores.routes import chores
    from .modules.chore_logs.routes import chore_logs
    from .modules.emails.routes import emails
    from .modules.single_use_endpoints.routes import single_use_endpoints

    for blueprint in [main, accounts, errors, lists, chores, chore_logs, emails, single_use_endpoints]:
        app.register_blueprint(blueprint)

    # login manager
    login_manager.init_app(app)
    # login_manager.session_protection = "strong"

    # email
    mail.init_app(app)

    # middleware
    @app.before_request
    def request_middleware():
        from main.modules.accounts.services import record_ip
        record_ip()

    # filter
    @app.template_filter()
    def day_of_week_str(raw):
        from utils import date_functions
        return date_functions.day_of_week_str(raw)

    @app.template_filter()
    def extract_date(date_or_datetime: date | datetime):
        from utils import date_functions
        return date_functions.extract_date(date_or_datetime)

    @app.template_filter()
    def number_suffix(value):
        if 10 <= value % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(value % 10, 'th')
        return f"{value}{suffix}"

        # return the app

    print("RUNNING APPLICATION")
    logger.debug("LOGGING IS RUNNING")
    logger.info(f"Running app in environment '{os.environ.get('ENVIRONMENT')}'")
    logger.info(f"FLASK_ENV: '{os.environ.get('FLASK_ENV')}'")
    return app


# Set up logging
logging.basicConfig()
logger = logging.getLogger("Chores")
logger.propagate = False
sh = logging.StreamHandler(sys.stdout)
sh.setFormatter(StreamLogFormatter())
fh = logging.FileHandler("application.log")
fh.setFormatter(FileLogFormatter())
logger.addHandler(sh)
logger.addHandler(fh)
logger.setLevel(logging.DEBUG if (
        os.environ.get('FLASK_ENV') == "dev" or os.environ.get("FLASK_ENV") == "development") else logging.INFO)
