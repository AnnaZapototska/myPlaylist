from flask import Blueprint, render_template, request, session, redirect, url_for
from app import db
from app.models.user import User
import hashlib

login_blueprint = Blueprint('login', __name__)


@login_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        user = User.query.filter_by(email=email, password=hashed_password).first()
        if user:
            session['loggedin'] = True
            session['userid'] = user.userid
            session['name'] = user.name
            session['email'] = user.email
            message = 'Logged in successfully!'
            return redirect(url_for('show_ytmusic_playlists'))  # Redirect to the playlists page
        else:
            message = 'Please enter correct email/password!'
    return render_template('login.html', message=message)


@login_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
        user_name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        account = User.query.filter_by(email=email).first()
        if account:
            message = 'Account already exists!'
        elif not validate_email(email):
            message = 'Invalid email address!'
        elif not user_name or not password or not email:
            message = 'Please fill out the form!'
        else:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            user = User(name=user_name, email=email, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            message = 'You have successfully registered!'
    elif request.method == 'POST':
        message = 'Please fill out the form!'
    return render_template('register.html', message=message)


def validate_email(email):
    return '@' in email and '.' in email
