import secrets
import urllib
import requests
from flask import redirect, session, request, url_for
from urllib import parse


def generate_session_id():
    # Generate a unique session ID (cookie value) using secrets module
    return secrets.token_hex(16)


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
        user_info_data = response.json()

        print("response", response)

        if 'id' in user_info_data:
            user_id = user_info_data['id']

            # Store the access token, refresh token, and user ID in the session
            session['access_token'] = access_token
            session['refresh_token'] = refresh_token
            session['user_id'] = user_id

            return redirect(url_for('show_ytmusic_playlists'))
        else:
            return "User ID not found in response."
    else:
        return "Error occurred during authentication."
