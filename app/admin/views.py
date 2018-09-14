from flask_admin import BaseView, expose, helpers
import flask_admin as admin
from flask_login import current_user
from flask import redirect, request
from ..models import Permission
from .forms import LoginForm
from flask_login import login_user
class MyView(admin.AdminIndexView):
	"""docstring for MyView"""
	@expose('/')
	def index(self):
		print 'indexaaa'
		if not current_user.can(Permission.ADMINISTER):
			
			return redirect(url_for('.login_view'))
		return self.render('admin/index.html')
	
	@expose('/login/', methods=('GET', 'POST'))
	def login_view(self):
		form = LoginForm(request.form)
		if helpers.validate_form_on_submit(form):
			user = form.get_user()
			login_user(user)

		if current_user.can(Permission.ADMINISTER):
			return redirect(url_for('.index'))
		self._template_args['form'] = form
		return super(MyView, self).index()
	def is_accessible(self):
		return current_user.can(Permission.ADMINISTER)