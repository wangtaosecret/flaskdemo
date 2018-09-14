# coding:utf8
#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Role, Permission, Post, Comment
from flask_script import Manager, Shell, Server
from flask_migrate import Migrate, MigrateCommand
from app.fake import users, posts
from flask_admin.contrib.sqla import ModelView
from app.admin.views import MyView
from app.flaskyModelView import UserModelView, PostModelView, CommentModelView
import flask_admin as admin
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)
admin = admin.Admin(app, u'管理后台', index_view=MyView(), base_template='admin/my_master.html', template_mode='bootstrap3')

admin.add_view(UserModelView(db.session, name=u'用户'))
admin.add_view(PostModelView(db.session, name=u'文章'))
admin.add_view(CommentModelView(db.session, name=u'评论'))
def make_shell_context():
	return dict(app=app, db=db, User=User, Role=Role, Permission=Permission, users=users, posts=posts, Post=Post)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)
# 添加这个可以局域网访问
manager.add_command('runserver', Server(host='0.0.0.0', port=5000))




COV = None
if os.environ.get('FLASK_COVERAGE'):
	import coverage
	COV = coverage.coverage(branch=True, include='app/*')
	COV.start()



@manager.command
def test(coverage=False):
	'''Run the unit tests.'''

	if coverage and not os.environ.get('FLASK_COVERAGE'):
		import sys
		os.environ['FLASKY_COVERAGE'] = '1'
		os.execvp(sys.executable, [sys.executable] + sys.argv)

	import unittest
	tests = unittest.TestLoader().discover('tests')
	unittest.TextTestRunner(verbosity=2).run(tests)

	if COV:
		COV.stop()
		COV.save()
		print('Coverage Summary:')
		basedir = os.path.abspath(os.path.dirname(__file__))
		covdir = os.path.join(basedir, 'tmp/coverage')
		COV.html_report(directory=covdir)
		print('HTML version: file://%s/index.html' % covdir)
		COV.erase()

if __name__ == '__main__':
	manager.run()