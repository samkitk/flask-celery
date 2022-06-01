from flask import Flask, flash, render_template, request, redirect, url_for
from celery import Celery
from dotenv import load_dotenv
import os
from flask_mail import Mail,Message

load_dotenv()

# print(os.environ.get("TEST_VAR"))
      
app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY")

app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379'

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = 'flask@example.com'


celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)


mail = Mail(app)
@celery.task
def send_mail(data):
    """ Function to send emails."""
    with app.app_context():
        msg = Message("Ping!",
                    sender="admin.ping",
                    recipients=[data['email']])
        msg.body = data['message']
        mail.send(msg)
    


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')

    elif request.method == 'POST':
        data = {}
        data['email'] = request.form['email']
        data['first_name'] = request.form['first_name']
        data['last_name'] = request.form['last_name']
        data['message'] = request.form['message']
        data['duration'] = int(request.form['duration'])
        data['duration_unit'] = request.form['duration_unit']
        duration_unit = data['duration_unit']
        
        if data['duration_unit'] == "1":
            data['duration'] *=60
            duration_unit = "minutes"
        elif data['duration_unit'] =="2":
            data['duration']*=3600
            duration_unit = "hours"
        elif data['duration_unit'] == "3":
            data['duration']*=86400
            duration_unit = "seconds"
            
        send_mail.apply_async(args=[data], countdown=data['duration'])
        flash(f"Email will be sent to {data['email']} in {request.form['duration']} {duration_unit}")
        return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)