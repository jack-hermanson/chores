from flask_bcrypt import Bcrypt
from flask import Flask
from flask_talisman import Talisman
from main.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user

bcrypt = Bcrypt()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "accounts.login"
login_manager.login_message_category = "warning"
migrate = Migrate(compare_type=True)


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
    # login_manager.init_app(app)

    # models
    from .modules.accounts import models
    from .modules.lists import models
    from .modules.chores import models
    from .modules.chore_logs import models

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

    for blueprint in [main, accounts, errors, lists, chores, chore_logs]:
        app.register_blueprint(blueprint)

    # login manager
    login_manager.init_app(app)
    login_manager.session_protection = "strong"

    # return the app
    print("RUNNING APPLICATION")
    return app
