import os
import base64

from flask import Flask, render_template, request, redirect, url_for, session

from model import Donation, Donor

app = Flask(__name__)

@app.route('/')
def home():
    return redirect(url_for('all'))

@app.route('/donations/')
def all():
    donations = Donation.select()
    return render_template('donations.jinja2', donations=donations)

@app.route('/add/', methods=['GET', 'POST']    )
def add():
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
        error = error,
        request = request
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6738))
    app.run(host='0.0.0.0', port=port)

