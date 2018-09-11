# coding:utf8
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User
class LoginForm(FlaskForm):
	email = StringField('Email', validators=[Required(), Length(1, 64),
		Email()])
	password = PasswordField('Password', validators=[Required()])
	remember_me = BooleanField('Keep me logged in')
	submit = SubmitField('Log in');




class RegistrationForm(FlaskForm):
	email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
	username = StringField('Username', validators=[Required(), Length(1, 64), 
		Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must have only letters, numbers,dots or underscores')])
	password = PasswordField('Password', validators=[Required(), EqualTo('password2', message='Passwords must match.')])
	password2 = PasswordField('Password2', validators=[Required()])
	submit = SubmitField('Register')
# 自定义验证函数
# 邮箱不能重复
	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('Email alreday registered.')
# 用户名不能重复
	def validate_username(self, field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError('Username already in use.')

# 修改密码
class ChangePasswordForm(FlaskForm):
	old_password = PasswordField('Old password', validators=[Required()])
	password = PasswordField('New password', validators=[Required(), EqualTo('password2',
		message='Passwords must match.')])
	password2 = PasswordField('Confirm new password', validators=[Required()])
	submit = SubmitField('Update Password')

# 发出重置密码请求道邮箱
class PasswordResetRequestForm(FlaskForm):
	email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
	submit = SubmitField('Reset Password')
# 重置密码
class PasswordResetForm(FlaskForm):
	password = PasswordField('New Password', validators=[Required(),
		EqualTo('password2', message='Passwords must match.')])
	password2 = PasswordField('Confirm password', validators=[Required()])
	submit = SubmitField('Reset Password')


class ChangeEmailForm(FlaskForm):
	email = StringField('New Email', validators=[Required(), Length(1, 64), Email()])
	password = PasswordField('Password', validators=[Required()])
	submit = SubmitField('Update Email Address')

	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('Email already registered.')
			


