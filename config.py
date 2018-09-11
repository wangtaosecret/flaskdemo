# coding:utf8
# 配置文件
import os
basedir = os.path.abspath(os.path.dirname(__file__))
# 基础配置类
class Config:
	# Flask-WTF能保护所有表单免受跨站请求伪造的攻击。为了实现CSRF保护，Flask-WTF需要程序设置一个秘钥

	SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
	FLASKY_MAIL_SENDER = 'Flasky Admin <flasky@example.com>'
	FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN') or '981760830@qq.com'
	FLASKY_POSTS_PER_PAGE = 20
	FLASKY_FOLLOWERS_PER_PAGE = 20
	FLASKY_COMMENTS_PER_PAGE = 50
	@staticmethod
	def init_app(app):
		pass
# 开发配置类
class DevelopmentConfig(Config):
	DEBUG = True
	MAIL_SERVER = 'smtp.163.com'
	MAIL_PORT = 25
	MAIL_USE_TLS = False
	MAIL_USE_SSL = False
	MAIL_USERNAME = 'wangtaosmail@163.com'
	MAIL_PASSWORD = 'xufei1111'
	# SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
	SQLALCHEMY_DATABASE_URI = 'mysql://root:xufei1111@localhost/flasky'

# 测试配置类
class TestingConfig(Config):
	TESTING = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')

# 生产配置类
class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data.sqlite')



config = {
	'development' : DevelopmentConfig,
	'testing' : TestingConfig,
	'production' : ProductionConfig,

	'default': DevelopmentConfig
}