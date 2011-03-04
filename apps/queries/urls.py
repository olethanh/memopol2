from django.conf.urls.defaults import patterns, url

from queries import views

urlpatterns = patterns('',
    url(r'^$', views.query, name='query'),
    url(r'^indexq$', views.indexquery, name='indexquery'),
)
