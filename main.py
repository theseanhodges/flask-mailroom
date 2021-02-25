import os
import base64

from flask import Flask, render_template, request, redirect, url_for, session
from passlib.hash import pbkdf2_sha256
from peewee import fn, JOIN

from model import Donation, Donor, User

app = Flask(__name__)
# Get the secret key from an environment variable, but set it to something random if it doesn't
# exist so that the app doesn't break.  However, sessions will be invalidated if this app re-runs,
# which isn't necessarily what we want.
app.secret_key = os.environ.get('FLASK_SESSION_KEY', os.urandom(24).hex())

@app.route('/')
def home():
    if not User.select():
        # Let the user create a new user account since there are none
        return redirect(url_for('new_user'))
    return redirect(url_for('all'))

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        # Redirect home if the user is already logged in
        return redirect(url_for('all'))
    error = ''
    if request.method == 'POST':
        user = User.select().where(User.username == request.form['username'])
        if user:
            user_record = user.get()
            if pbkdf2_sha256.verify(request.form['password'], user_record.password):
                session['username'] = user_record.username
                return redirect(url_for('all'))
        error = 'Invalid login.'
    return render_template(
        'login.jinja2',
        error=error,
        request=request,
        username=session['username'] if 'username' in session.keys() else ''
    )

@app.route('/logout/')
def logout():
    session.pop('username')
    return redirect(url_for('all'))

@app.route('/newuser/', methods=['GET', 'POST'])
def new_user():
    """
    Allow creation of a new user if:
    1. No users exist, or
    2. A valid user is logged in.
    I need to cut this short at some point but the next step would be to differentiate user levels
    and only allow superusers to do this.
    """
    error = ''
    if User.select():
        if 'username' in session.keys():
            if not User.select().where(User.username == session['username']):
                # We have a valid session but the user is not in the DB
                # For now this is an unexpected edge case since there's no functionality to delete
                # users, but...
                return redirect(url_for('all'))
        else:
            return redirect(url_for('all'))
    if request.method == 'POST':
        if request.form['username'] == '' or request.form['password'] == '':
            error = 'All fields are required.'
        elif request.form['password'] != request.form['confirm']:
            error = 'Passwords do not match.'
        elif User.select().where(User.username == request.form['username']):
            error = 'User already exists.'
        else:
            User(
                username=request.form['username'],
                password=pbkdf2_sha256.hash(request.form['password'])
            ).save()
            return redirect(url_for('all'))
    return render_template(
        'new_user.jinja2',
        error=error,
        request=request,
        username=session['username'] if 'username' in session.keys() else ''
    )

@app.route('/donations/')
def all():
    if request.args.get('donor') != '' and request.args.get('donor') is not None:
        donations = Donation.select().where(Donation.donor == request.args.get('donor'))
    else:
        donations = Donation.select()
    donors = Donor.select()
    return render_template(
        'donations.jinja2',
        donations=donations,
        donors=donors,
        request=request,
        username=session['username'] if 'username' in session.keys() else ''
    )

@app.route('/report/')
def report():
    donations = Donor.select(
        Donor,
        fn.Count(Donation.value).alias('count'),
        fn.Sum(Donation.value).alias('sum')
    ).join(
        Donation,
        JOIN.LEFT_OUTER
    ).group_by(
        Donor
    )
    return render_template(
        'report.jinja2',
        donations=donations,
        request=request,
        username=session['username'] if 'username' in session.keys() else ''
    )

@app.route('/add/', methods=['GET', 'POST'])
def add():
    if 'username' not in session:
        return redirect(url_for('login'))
    error = ''
    if request.method == 'POST':
        try:
            donation = float(request.form['value'])
        except ValueError:
            pass
        else:
            if request.form['donor'] != '' and donation > 0:
                if not Donor.select().where(Donor.name == request.form['donor']):
                    Donor(
                        name=request.form['donor']
                    ).save()
                Donation(
                    donor=request.form['donor'],
                    value=donation
                ).save()
                return redirect(url_for('all'))
        error = 'A donor name and a positive, non-zero donation amount are required.'
    return render_template(
        'new_donation.jinja2',
        error=error,
        request=request,
        username=session['username'] if 'username' in session.keys() else ''
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6738))
    app.run(host='0.0.0.0', port=port)
