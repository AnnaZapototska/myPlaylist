from flask import Flask, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from ytmusicapi import YTMusic

db = SQLAlchemy()
ytmusic = None  # Global variable to hold the YTMusic client object


def create_app():
    app = Flask(__name__)
    app.secret_key = 'xyzsdfg'
    app.config[
        'SQLALCHEMY_DATABASE_URI'] = 'postgresql://my_playlist_db_user:EtHWfr5hUqZDgchZYjxMGxTVs8kntOhZ@dpg-chocr6m7avja2d8c50n0-a.oregon-postgres.render.com/my_playlist_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the database
    db.init_app(app)

    # Import and register your blueprints
    from app.controllers.login import handle_login, handle_register
    app.register_blueprint(handle_login)
    app.register_blueprint(handle_register)

    # Define your routes
    @app.route('/')
    def home():
        return redirect(url_for('login.login'))

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login.login'))

    @app.teardown_appcontext
    def teardown_appcontext(error):
        db.session.remove()

    with app.app_context():
        db.create_all()
        initialize_ytmusic_client()

    return app


def initialize_ytmusic_client():
    global ytmusic

    # Initialize the YTMusic client
    ytmusic = YTMusic()

    # You can now use the 'ytmusic' object to interact with the YouTube Music API

