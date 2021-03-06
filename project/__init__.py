import os
from flask_sock import Sock
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


def load_events():
    from . import events


# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
sock = Sock()
load_dotenv()
load_events()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'SQLALCHEMY_DATABASE_URI')
    app.config['SOCK_SERVER_OPTIONS'] = {'ping_interval': 25}
    app.config['AUTH_PAGE_URL'] = os.getenv('AUTH_PAGE_URL')
    app.config['TOKEN'] = os.getenv('TOKEN')
    app.config['SOCK_PROTOCOL'] = os.getenv('SOCK_PROTOCOL')
    app.config['DEVELOPMENT'] = os.getenv('DEVELOPMENT')

    db.init_app(app)
    sock.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
