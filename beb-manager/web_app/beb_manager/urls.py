from django.conf.urls import include, url
from django.contrib.auth import views as auth_views

from . import views

app_name = "beb_manager"

registration_patterns = [
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'beb_manager:login'}, name='logout'),
    url(r'^signup/$', views.signup, name='signup'),
]

urlpatterns = [
	url(r'^$', views.boards, name='boards'),
	url(r'^accounts/', include(registration_patterns)),
]