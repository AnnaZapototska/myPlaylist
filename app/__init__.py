import secrets
import urllib
from urllib import parse

import requests
from flask import Flask, redirect, url_for, session, request, render_template
from flask_sqlalchemy import SQLAlchemy
from ytmusicapi import YTMusic
import json

db = SQLAlchemy()
ytmusic = None  # Global variable to hold the YTMusic client object


def generate_session_id():
    # Generate a unique session ID (cookie value) using secrets module
    return secrets.token_hex(16)


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
        if 'access_token' not in session or 'user_id' not in session:
            return redirect(url_for('login.login'))

        try:
            # Get the access token and user ID from the session
            access_token = session['access_token']
            user_id = session['user_id']
            session_id = session.get('session_id')  # Retrieve the unique session ID (cookie value)

            print(f"User id: {user_id}")
            print(f"Access Token: {access_token}")
            print(f"Session ID: {session_id}")

            # Initialize the YTMusic client with the user ID
            global ytmusic
            ytmusic = YTMusic()
            ytmusic.setup(filepath=".headers_auth.json",
                          headers_raw=f"Authorization: Bearer {access_token}\nCookie: session_id={session_id}\nx-goog-authuser: {user_id}")

            # Get the user's playlists
            playlists = ytmusic.get_library_playlists(limit=None)

            # Process the playlists data or render a template
            return render_template('ytmusic_playlists.html', playlists=playlists)

        except Exception as e:
            import traceback
            print(f"Error: {e}")
            traceback.print_exc()
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

        # Generate and set a unique session ID (cookie value)
        session['session_id'] = generate_session_id()

        return redirect(auth_redirect)

    @app.route('/ytmusic/callback')
    def handle_ytmusic_callback():
        code = request.args.get('code')

        # Exchange the authorization code for an access token
        token_url = 'https://oauth2.googleapis.com/token'
        token_params = {
            'client_id': '866143699543-g80lda2kbtp9ci0gskh3em31vvf2t0l0.apps.googleusercontent.com',
            'client_secret': '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',
            'redirect_uri': 'https://my-playlist-project.onrender.com/ytmusic/callback',
            'code': code,
            'grant_type': 'authorization_code',
        }

        response = requests.post(token_url, data=token_params)

        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data['access_token']
            refresh_token = token_data['refresh_token']

            # Get the user's ID from the access token
            user_info_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
            headers = {'Authorization': 'Bearer ' + access_token}
            response = requests.get(user_info_url, headers=headers)
            print("User data", requests.get(user_info_url, headers=headers))
            user_info_data = response.json()
            print("User data", response)

            if 'id' in user_info_data:
                user_id = user_info_data['id']
                print("User ID:", user_id)
                # Store the access token, refresh token, and user ID in the session
                session['access_token'] = access_token
                session['refresh_token'] = refresh_token
                session['user_id'] = user_id

                print("check 3")

                return redirect(url_for('show_ytmusic_playlists'))
            else:
                return "User ID not found in response."
        else:
            return "Error occurred during authentication."

    @app.teardown_appcontext
    def teardown_appcontext(error):
        db.session.remove()

    with app.app_context():
        db.create_all()

    return app
