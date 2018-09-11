# coding:utf8
from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail
def send_async_email(app, msg):
	with app.app_context():
		mail.send(msg)
# to 收件人地址 subject 邮件主题 template 发送模板 
def send_email(to, subject, template, **kwargs):
	app = current_app._get_current_object()
	msg = Message(current_app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject, 
		sender=app.config['MAIL_USERNAME'], recipients=[to])
	msg.body = render_template(template + '.txt', **kwargs)
	msg.html = render_template(template + '.html', **kwargs)
	# mail.send(msg)
	thr = Thread(target=send_async_email, args=[app, msg])
	thr.start()
	return thr