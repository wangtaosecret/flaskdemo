# coding:utf8
# 由于这种认证方法只在API蓝本中使用，所以Flask-HTTPAuth扩展只在
# 蓝本包中初始化，而不像其他扩展哪样需要在程序包中初始化
from flask import g, jsonify, request
from flask_httpauth import HTTPBasicAuth
from ..models import User
from . import api
from .errors import unauthorized, forbidden

auth = HTTPBasicAuth()

# api登录功能
@api.route('/login')
def login():
	username = request.args.get('username', '')
	password = request.args.get('password', '')

	if username is None or password is None:
		return jsonifyy({'statuscode': 400,
						'msg': '账号或密码错误'})

	loginSuccess = verify_password(username, password)
	print g.current_user.is_authenticated
	if loginSuccess:
		return jsonify({'statuscode': 200, 
					'msg': 'login success',
					'token': g.current_user.generate_auth_token(expiration=3600), 'expiration': 3600})
	else:
		return jsonify({'statuscode': 401, 
					'msg': 'login failed'})

# 认证用户使用账号密码或者令牌
@auth.verify_password
def verify_password(email_or_token, password):
	if email_or_token == '':
		# g.current_user = AnonymouseUser()
		return False

	if password == '':
		g.current_user = User.verify_auth_token(email_or_token)
		g.token_used = True
		return g.current_user is not None

	user = User.query.filter_by(email=email_or_token).first()
	if not user:
		return False
	g.current_user = user
	g.token_used = False
	return user.verify_password(password)


@auth.error_handler
def auth_error():
	return unauthorized('Invalid credentials')

# 保护路由
@api.before_request
@auth.login_required
def before_request():
	if not g.current_user.is_anonymous and \
		not g.current_user.confirmed:
		return forbidden('Unconfirmed account')

# 获取认证令牌
@api.route('/tokens/', methods=['POST'])
def get_token():
	if g.current_user.is_anonymous or g.token_used:
		return unauthorized('Invalid credentials')

	return jsonify({'token': g.current_user.generate_auth_token(expiration=3600), 'expiration': 3600})
