from django.conf.urls.defaults import *
from geek.forum.views import *

urlpatterns = patterns('',
    url(r'^$', home),
    url(r'^(?P<forum_id>\d+)/$', forum),
    url(r'^(?P<forum_id>\d+)/(?P<thread_id>\d+)/$', thread),
    url(r'^(?P<forum_id>\d+)/new/$', new_thread),
    url(r'^(?P<forum_id>\d+)/(?P<thread_id>\d+)/edit/$', edit_thread),
    url(r'^(?P<forum_id>\d+)/(?P<thread_id>\d+)/reply/$', reply),
    url(r'^edit-reply/(?P<reply_id>\d+)/$', edit_reply),
    url(r'^search-thread/$', search_thread),
    url(r'^elited-thread/$', elited_thread),
    url(r'^my-threads/$', my_threads),
    url(r'^at-me/$', at_me),
    url(r'^readed-at-me/(?P<news_id>\d+)/$', readed_news),
    url(r'^delete-at-me/(?P<news_id>\d+)/$', delete_news),
    url(r'^new-at-num/$', new_at_num),
    url(r'^nearest-users/$', nearest_users),
)
