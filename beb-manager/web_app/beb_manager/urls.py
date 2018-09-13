from django.conf.urls import include, url
from django.contrib.auth import views as auth_views

from . import views

app_name = "beb_manager"

registration_patterns = [
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'beb_manager:login'}, name='logout'),
    url(r'^signup/$', views.signup, name='signup'),
]

concrete_board_patterns = [
    # url(r'^$', views.tasks, name='tasks'),
    url(r'^edit/$', views.edit_board, name='edit_board'),
    url(r'^delete/$', views.delete_board, name='delete_board'),
    # url(r'^task_list/', include(task_lists_patterns)),
    # url(r'^task/(?P<task_id>[0-9]+)/', include(exact_task_patterns)),
    # url(r'^plan/', include(plans_patterns)),
    # url(r'^user/', include(users_patterns))
]

board_patterns = [
    url(r'^$', views.boards, name='boards'),
    url(r'^(?P<board_id>[0-9]+)/', include(concrete_board_patterns)),
    url(r'^add/$', views.add_board, name='add_board'),
]

urlpatterns = [
    url(r'^', include(board_patterns)),
    url(r'^accounts/', include(registration_patterns)),
]
