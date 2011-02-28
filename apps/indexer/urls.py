from django.conf.urls.defaults import patterns, url

import views

urlpatterns = patterns('',
    url(r'^update/meps/(?P<mep_id>\w+)/$', views.update_mep, name='update_mep'),
    url(r'^update/mps/(?P<mep_id>\w+)/$', views.update_mp, name='update_mp'),
    url(r'^update/votes/(?P<mep_id>\w+)/$', views.update_vote, name='update_vote'),
)
