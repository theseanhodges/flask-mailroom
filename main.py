import os
import base64

from flask import Flask, render_template, request, redirect, url_for, session
from passlib.hash import pbkdf2_sha256

from model import Donation, Donor, User

app = Flask(__name__)
# Get the secret key from an environment variable, but set it to something random if it doesn't
# exist so that the app doesn't break.  However, sessions will be invalidated if this app re-runs,
# which isn't necessarily what we want.
app.secret_key = os.environ.get('FLASK_SESSION_KEY', os.urandom(24).hex())

@app.route('/')
def home():
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
