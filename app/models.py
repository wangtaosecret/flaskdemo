# coding:utf8
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import UserMixin, AnonymousUserMixin
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request, url_for
from datetime import datetime
import hashlib
from markdown import markdown
import bleach
from app.exceptions import ValidationError
# 权限
class Permission:
	FOLLOW = 1
	COMMENT = 2
	WRITE_ARTICLES = 4
	MODERATE_COMMENTS = 8
	ADMINISTER = 16

class Role(db.Model):
	"""docstring for Role"""
	__tablename__ = 'roles'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	# 只有一个角色的default字段要设为True，其他都设为False。用户注册时其角色会被设为默认角色。
	default = db.Column(db.Boolean, default=False, index=True)
	permissions = db.Column(db.Integer)
	users = db.relationship('User', backref='role', lazy='dynamic')
	def __repr__(self):
		return '<Role %r>' % self.name

	@staticmethod
	def insert_roles():
		roles = {
			'User': (Permission.FOLLOW |
					 Permission.COMMENT |
					 Permission.WRITE_ARTICLES, True),
			'Moderator': (Permission.FOLLOW | 
						  Permission.COMMENT |
						  Permission.WRITE_ARTICLES | 
						  Permission.MODERATE_COMMENTS, False),
			'Administrator': (0xff, False)
		}

		for r in roles:
			role = Role.query.filter_by(name=r).first()
			if role is None:
				role = Role(name=r)
			role.permissions = roles[r][0]
			role.default = roles[r][1]
			db.session.add(role)

		db.session.commit()


class Comment(db.Model):
	__tablename__ = 'comments'
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.Text)
	body_html = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	disabled = db.Column(db.Boolean)
	author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

	@staticmethod
	def on_change_body(target, value, oldvalue, initiator):
		allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i', 'strong']
		target.body_html = bleach.linkify(bleach.clean(
			markdown(value, output_format='html'),
			tags=allowed_tags, strip=True
			))

db.event.listen(Comment.body, 'set', Comment.on_change_body)

class Post(db.Model):
	__tablename__ = 'posts'
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.Text)
	timestamp = db.Column(db.DateTime(), index=True, default=datetime.utcnow)
	author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	body_html = db.Column(db.Text)
	comments = db.relationship('Comment', backref='post', lazy='dynamic')

	@staticmethod
	def on_change_body(target, value, oldvalue, initiator):
		allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
						'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
						'h1', 'h2', 'h3', 'p']

		target.body_html = bleach.linkify(bleach.clean(
			markdown(value, output_format='html'),
			tags=allowed_tags, strip=True
			))	

	@staticmethod
	def from_json(json_post):
		body = json_post.get('body')
		if body is None or body=='':
			raise ValidationError('post does not have a body')

		return Post(body=body)
	def to_json(self):
		json_post = {
			'url': url_for('api.get_post', id=self.id, _external=True),
			'body': self.body,
			'body_html': self.body_html,
			'timestamp': self.timestamp,
			'author': url_for('api.get_user', id=self.author_id, _external=True),
			'comments': url_for('api.get_post_comments', id=self.id, _external=True),
			'comment_count': self.comments.count()
		}
		return json_post

# 监听Postbody 的改变，改变之后调用on_change_body函数
db.event.listen(Post.body, 'set', Post.on_change_body)
	# @staticmethod
	# def generate_fake(count=100):
	# 	from random import seed, randint
	# 	import forgery_py

	# 	seed()
	# 	user_count = User.query.count()
	# 	for i in range(count):
	# 		u = User.query.offset(randint(0, user_count - 1)).first()
	# 		p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
	# 			timestamp=forgery_py.date.date(True),
	# 			author=u)
	# 		db.session.add(p)
	# 		db.session.commit()

class Follow(db.Model):
	__tablename__ = 'follows'
	follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
								  primary_key=True)
	followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
								primary_key=True)

	timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(UserMixin, db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(64), unique=True, index=True)
	username = db.Column(db.String(64), unique=True, index=True)
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
	password_hash = db.Column(db.String(128))
	confirmed = db.Column(db.Boolean, default=False)

	name = db.Column(db.String(64))
	location = db.Column(db.String(64))
	about_me = db.Column(db.Text())
	member_since = db.Column(db.DateTime(), default=datetime.utcnow)
	last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

	avatar_hash = db.Column(db.String(32))
	# lazy 指定如何加载相关记录。可选值有select（首次访问时按需加载）
	# immediate（源对象加载后就加载）
	# joined（加载记录，但使用联结）
	# subquery（立即加载，但使用子查询）
	# noload（永不加载）和dynamic（不加载记录，但提供加载记录的查询）
	posts = db.relationship('Post', backref='author', lazy='dynamic')


	followed = db.relationship('Follow',
								foreign_keys=[Follow.follower_id],
								backref=db.backref('follower', lazy='joined'),
								lazy='dynamic',
								cascade='all, delete-orphan')
	followers = db.relationship('Follow',
								foreign_keys=[Follow.followed_id],
								backref=db.backref('followed', lazy='joined'),
								lazy='dynamic',
								cascade='all, delete-orphan')


	comments = db.relationship('Comment', backref='author', lazy='dynamic')


	def to_json(self):
		json_user = {
			'url': url_for('api.get_post', id=self.id, _external=True),
			'username': self.username,
			'member_since': self.last_seen,
			'posts': url_for('api.get_user_posts', id=self.id, _external=True),
			'followed_posts': url_for('api.get_user_followed_posts', id=self.id, _external=True),
			'post_count': self.posts.count()

		}
		return json_user

	# 生成认证令牌
	def generate_auth_token(self, expiration):
		s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
		return s.dumps({'id': self.id})
	# 验证令牌
	@staticmethod
	def verify_auth_token(token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return None
		return User.query.get(data[id])

# 添加自己关注自己
	@staticmethod
	def add_self_follows():
		for user in User.query.all():
			if not user.is_following(user):
				user.follow(user)
				db.session.add(user)
				db.session.commit()
	# 注意，followed_posts() 方法定义为属性，因此调用时无需加 ()。如此一来，所有关系的 句法都一样了。
	@property
	def followed_posts(self):
		return Post.query.join(Follow, Follow.followed_id == Post.author_id).filter(Follow.follower_id==self.id)
	# 关注
	def follow(self, user):
		if not self.is_following(user):
			f = Follow(follower=self, followed=user)
			db.session.add(f)
	# 取消关注
	def unfollow(self, user):
		f = self.followed.filter_by(followed_id=user.id).first()
		if f:
			db.session.delete(f)
	# 是否正在关注用户user
	def is_following(self, user):
		return self.followed.filter_by(followed_id=user.id).first() is not None
	# user是否正在关注自己
	def is_followed_by(self, user):
		return self.followers.filter_by(follower_id=user.id).first() is not None
	def ping(self):
		self.last_seen = datetime.utcnow()
		db.session.add(self)

	def gravatar_hash(self):
		return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

	def gravatar(self, size=100, default='identicon', rating='g'):
		if request.is_secure:
			url = 'https://secure.gravatar.com/avatar'
		else:
			url = 'http://www.gravatar.com/avatar'
		hash = self.avatar_hash or self.gravatar_hash()
		return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=hash, size=size, default=default, rating=rating)

#  这里的两个时间默认值都是接收的函数，每次需要生成默认值时，调用指定的函数
	def __init__(self, **kwargs):
		super(User, self).__init__(**kwargs)
		if self.role is None:
			if self.email == current_app.config['FLASKY_ADMIN']:
				self.role = Role.query.filter_by(permissions=0xff).first()
			if self.role is None:
				self.role = Role.query.filter_by(default=True).first()

		if self.email is not None and self.avatar_hash is None:
			self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
		self.follow(self)


	def generate_confirmation_token(self, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'confirm': self.id})

	def generate_reset_token(self, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'reset': self.id}).decode('utf-8')

	def generate_email_change_token(self, new_email, expiration=3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps(
			{'change_email': self.id, 'new_email':new_email}
			
			).decode('utf-8')
	def change_email(self, token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token.encode('utf-8'))
		except:
			return False
		if data.get('change_email') != self.id:
			return False
		new_email = date.get('new_email')
		if new_email is None:
			return False

		if self.query.filter_by(email=new_email).first() is not None:
			return False
		self.email = new_email
		self.avatar_hash = self.gravatar_hash()
		db.session.add(self)
		return True

	@staticmethod
	def reset_password(token, new_password):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token.encode('utf-8'))
		except:
			return False

		user = User.query.get(data.get('reset'))
		if user is None:
			return False

		user.password = new_password
		db.session.add(user)
		return True

	def confirm(self, token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('confirm') != self.id:
			return False
		self.confirmed = True
		db.session.add(self)
		db.session.commit()
		return True

	@property
	def password(self):
		raise AttributeError('password is not a readable attribute')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)


	def can(self, permissions):
		return self.role is not None and (self.role.permissions & permissions) == permissions

	def is_administrator(self):
		return self.can(Permission.ADMINISTER)


	def __repr__(self):
		return '<User %r>' % self.username


	# @staticmethod
	# def generate_fake(count=100):
	# 	from sqlalchemy.ext import IntegrityError
	# 	from random import seed
	# 	import forgery_py

	# 	seed()
	# 	for i in range(count):
	# 		u = User(email=forgery_py.internet.email_address(),
	# 			username=forgery_py.internet.user_name(True),
	# 			password=forgery_py.lorem_ipsum.word(),
	# 			confirmed=True,
	# 			name=forgery_py.name.full_name(),
	# 			location=forgery_py.address.city(),
	# 			about_me=forgery_py.lorem_ipsum.sentence(),
	# 			member_since=forgery_py.date.date(True))
	# 		db.session.add(u)
	# 		try:
	# 			db.session.commit()
	# 		except IntegrityError:
	# 			db.session.rollback()

# 出于一致性考虑，我们还定义了 AnonymousUser 类，
# 并实现了 can() 方法和 is_administrator() 方法。
# 这个对象继承自 Flask-Login 中的 AnonymousUserMixin 类，
# 并将其设为用户未登录时 current_user 的值。
# 这样程序不用先检查用户是否登录，就能自由调用
#  current_user.can() 和 current_user.is_administrator()。
class AnonymouseUser(AnonymousUserMixin):
	def can(self, permissions):
		return False
	def is_administrator(self):
		return False

login_manager.anonymous_user = AnonymouseUser
# 使用Flask-Login要求程序实现一个回调函数，使用指定的标识符加载用户
#  加载用户的回调函数接收以Unicode字符串形式表示的用户标识符
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))











