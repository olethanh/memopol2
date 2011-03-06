from django.conf.urls.defaults import patterns, url

from models import MEP, Group, Country

names_dict = {'queryset' : MEP.view('meps/by_name'), 'template_name' : 'index.html', 'template_object_name':'meps' }
groups_dict = {'queryset': Group.view('meps/groups', group=True), 'template_object_name':'groups', 'order_by':'-count'}
countries_dict = {'queryset': Country.view('meps/countries', group=True), 'template_object_name':'countries', 'order_by':'-count'}

urlpatterns = patterns('meps.views',
    url(r'^names/$', 'documents_list', names_dict, name='index_names',),
    url(r'^countries/$', 'documents_list', countries_dict, name='index_countries'),
    url(r'^country/(?P<country_code>[a-zA-Z][a-zA-Z])/$', 'index_by_country', name='index_by_country'),
    url(r'^groups/$', 'documents_list', groups_dict, name='index_groups'),
    url(r'^group/(?P<group>[a-zA-Z/-]+)/$', 'index_by_group', name='index_by_group'),
    url(r'^mep/(?P<mep_id>\w+)/$', 'mep', name='mep'),
    url(r'^mep/(?P<mep_id>\w+)/raw/$', 'mep_raw', name='mep_raw'),
    url(r'^mep/(?P<mep_id>\w+)/json/$', 'mep_json', name='mep_json'),
    url(r'^mep/(?P<mep_id>\w+)/addposition/$', 'mep_addposition', name='mep_addposition'),

    url(r'^moderation/$', 'moderation', name='moderation'),
    url(r'^moderation/get_unmoderated_positions$', 'moderation_get_unmoderated_positions', name='moderation_get_unmoderated_positions'),
    url(r'^moderation/moderate_position$', 'moderation_moderate_positions', name='moderation_moderate_positions'),
)

