import os
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
load_dotenv()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'SQLALCHEMY_DATABASE_URI')

    db.init_app(app)
    socketio = SocketIO(app)
    socketio.run(app)

    from .models import Book

    @socketio.on('get download url')
    def handle_get_download_url(json):
        book = db.session.query(Book).filter_by(
            record_id=json['record_id']).first()
        json = {
            'ereaderuid': json['ereaderuid'],
            'url': book.content
        }
        print(json)
        emit('download', json)

    @socketio.on('status_req')
    def status_req():
        emit('status_req')

    @socketio.on('status_res')
    def status_res(json):
        emit('status_res', json)

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
