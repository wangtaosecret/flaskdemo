# coding:utf8
from flask_admin.contrib.sqla import ModelView
from flask_admin import expose
from .models import User, Post, Comment
from flask_admin.model.template import EndpointLinkRowAction, LinkRowAction
from wtforms.fields import SelectField
class UserModelView(ModelView):

	column_labels = {
		'id': u'编号',
		'role_id': u'角色',
		'email': u'邮箱\用户名',
		'username': u'用户名',
		'confirmed': u'邮箱验证',
		'name': u'真实名字',
		'location': u'地址',
		'about_me': u'个性签名',
		'member_since': u'注册日期',
		'last_seen': u'最后登录',
		# 'posts': u'文章',
		# 'followed': u'关注',
		# 'followers': u'粉丝',
		# 'comments': u'评论',
		'role': u'用户角色'
	}
	# inline_models = （）
	# 是否允许创建、删除、编辑、只读
	can_create = True
	# can_delete = False
	# can_edit = False
	# can_view_details = True
	# 每一页显示行数
	page_size = 20;
	# 直接在视图中启动内联编辑，快速编辑行
	column_editable_list = ['name', 'username','about_me', 'location', 'role_id']

	#搜索列表
	column_searchable_list = ['username', 'name']
	# 筛选列表
	column_filters = ['location']

	form_columns = ['posts', 'id', 'followed', 'followers', 'comments']


	column_list = ('id', 'role', 'email', 'username', 'confirmed', 'name', 'location', 'about_me', 'member_since', 'last_seen')
	def __init__(self, session, **kwargs):
		super(UserModelView, self).__init__(User, session, **kwargs)

	# form_overrides = dict(role_id=SelectField)
	form_choices = dict(
			role_id = dict(choices = [(0, 'User'), (1, 'Moderator'), (2, 'Administrator')]))

	# 当表单包含外键时，使用Ajax加载那些相关的模型（没会用）
	# form_ajax_refs = {
 #        'posts': {
 #            'fields': (Post.id, Post.timestamp),
 #            'page_size': 10,
 #        }
 #    }

    #删除行
    # column_exclude_list = []
# 	class postLink(LinkRowAction):
# 		def render(self, context, row_id, row):
# 			m = self._resolve_symbol(context, 'row_actions.link')
# 			if isinstance(self.url, str):
# 				row_group_id = row_group_id
# 				url = self.url.format(row_id=row_id, row_group_id=row_group_id)
# 			else:
# 				url = self.url(self, row_id, row)
# 			return m(self, url)

# 	column_extra_row_actions = [
# #注意图标生成在原有的编辑和删除的小图标后面,先根据外链的id拼出url
#         postLink('glyphicon glyphicon-user', '/admin/group/edit/?url=%2Fadmin%2Fgroup%2F&id={row_group_id}'),
#         EndpointLinkRowAction('glyphicon glyphicon-test', 'user.index_view')
#     ]

class PostModelView(ModelView):
	column_labels = {
		'body': u'文章内容',
		'timestamp': u'发布时间',
		'body_html': u'网页显示内容',
		'author': u'作者',
		'comments': u'评论'
	}
	#搜索列表
	column_searchable_list = ['body', 'author_id']
	# column_list = ('id', 'role_id', 'email', 'username', 'confirmed', 'name', 'location', 'about_me', 'member_since', 'last_seen')
	def __init__(self, session, **kwargs):
		super(PostModelView, self).__init__(Post, session, **kwargs)

class CommentModelView(ModelView):
	#搜索列表
	column_searchable_list = ['body']
	def __init__(self, session, **kwargs):
		super(CommentModelView, self).__init__(Comment, session, **kwargs)
