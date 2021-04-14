from threading import Thread
import flask
from flask_mail import Mail, Message

mail = Mail()


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipient, text_body, html_body):
    msg = Message(subject=subject, sender=sender, recipients=[recipient], body=text_body, html=html_body)
    app = flask.current_app._get_current_object()
    Thread(target=send_async_email, args=(app, msg)).start()


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[iTurmas] Nova senha',
               sender=flask.current_app.config['ADMIN_EMAIL'],
               recipient=user.email,
               text_body=flask.render_template('email/reset_password.txt',
                                               user=user, token=token),
               html_body=flask.render_template('email/reset_password.html',
                                               user=user, token=token))
