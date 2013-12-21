from django.conf.urls.defaults import *
from geek.geekchallenge.views import *
from geek import forum
import os

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', home),
    url(r'^accounts/login/$', team_login),
    url(r'^accounts/logout/$', team_logout),
    url(r'^accounts/register/$', register),
    url(r'^accounts/confirm/(?P<activation_code>\w{40})/$', confirm),
    url(r'^accounts/forget-password/$', forget_password),
    url(r'^accounts/reset-password/(?P<reset_password_code>\w{40})/$', reset_password),
    url(r'^accounts/change-password/$', change_password),
    url(r'^team-info/$', team_info),
    url(r'^rules/$', rules),
    url(r'^challenge/$', challenge),
    url(r'^challenge/type-(?P<type_id>\d+)/$', challenge),
    url(r'^rank/$', rank),
    url(r'^notices/$', show_notices),
    url(r'^admin/team-info/$', admin_team_info),
    url(r'^admin/item-info/$', admin_item_info),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^forum/', include('geek.forum.urls')),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root':os.path.dirname(os.path.realpath(__file__))+'/geekchallenge/static/'}), 
    )
