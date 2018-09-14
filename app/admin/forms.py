# coding:utf8
from wtforms import StringField, PasswordField, BooleanField, SubmitField	
from ..models import User
from wtforms.validators import Required
from wtforms import form, fields, validators
from flask_login import login_user
class LoginForm(form.Form):
	login = StringField(lable=u'管理员账号', validators=[Required()])
	password = PasswordField(label=u'密码', validators=[Required()])

	def validate_login(self, field):
		user = self.get_user()
		if user is None:
			raise validators.ValidationError(u'账号不存在')
			if not user.verify_password(self.password.data):
				raise validators.ValidationError(u'密码错误')
			
	def get_user(self):
		return User.query.filter_by(email=self.login.data).first()