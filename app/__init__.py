import urllib
import requests
from flask import Flask, redirect, url_for, session, request, render_template
from flask_sqlalchemy import SQLAlchemy
from ytmusicapi import YTMusic
from urllib import parse

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

    @app.route('/ytmusic/playlists')
    def show_ytmusic_playlists():
        if 'access_token' not in session:
            return redirect(url_for('login.login'))

        try:
            # Get the access token from the session
            access_token = session['access_token']

            # Initialize the YTMusic client
            ytmusic = YTMusic()
            ytmusic.headers['Authorization'] = f'Bearer {access_token}'

            # Get the user's playlists
            playlists = ytmusic.get_library_playlists(limit=None)  # Retrieve all playlists

            # Process the playlists data or render a template
            return render_template('ytmusic_playlists.html', playlists=playlists)

        except Exception as e:
            print(f"Error: {e}")
            return "An error occurred while retrieving playlists. Please try again later."

    @app.route('/ytmusic/auth')
    def authenticate_ytmusic():
        # Redirect the user to YouTube for authentication
        auth_url = 'https://accounts.google.com/o/oauth2/auth'
        params = {
            'client_id': '866143699543-g80lda2kbtp9ci0gskh3em31vvf2t0l0.apps.googleusercontent.com',
            'redirect_uri': request.url_root + 'ytmusic/callback',
            'scope': 'https://www.googleapis.com/auth/youtube.force-ssl',
            'response_type': 'code',
            'access_type': 'offline',
            'prompt': 'consent',
        }
        auth_redirect = auth_url + '?' + urllib.parse.urlencode(params)
        return redirect(auth_redirect)

    @app.route('/ytmusic/callback')
    def handle_ytmusic_callback():
        # Handle the callback from YouTube after authentication
        auth_code = request.args.get('code')

        # Exchange the authorization code for an access token
        token_endpoint = 'https://accounts.google.com/o/oauth2/token'
        data = {
            'code': auth_code,
            'client_id': '866143699543-g80lda2kbtp9ci0gskh3em31vvf2t0l0.apps.googleusercontent.com',
            'client_secret': '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',
            'redirect_uri': request.url_root + 'ytmusic/callback',
            'grant_type': 'authorization_code'
        }
        response = requests.post(token_endpoint, data=data)
        token_data = response.json()
        access_token = token_data.get('access_token')

        # Store the access token in the session for future use
        session['access_token'] = access_token

        return redirect(url_for('show_ytmusic_playlists'))

    @app.teardown_appcontext
    def teardown_appcontext(error):
        db.session.remove()

    with app.app_context():
        db.create_all()

    return app
