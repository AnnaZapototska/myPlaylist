from flask import Blueprint, render_template, request, session
from app import db
from app.models.user import User

handle_playlist = Blueprint('playlist', __name__)


@handle_playlist.route('/playlist')
def playlist():
    # Retrieve and display user's playlists
    # Implement authentication check before accessing this page
    return render_template('playlist.html')
