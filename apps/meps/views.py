import time
from os.path import realpath
from datetime import datetime

import simplejson

from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import get_object_or_404
from django.core import serializers
from django.conf import settings
from django.views.generic.simple import direct_to_template
from django.contrib.admin.views.decorators import staff_member_required

from meps.models import MEP, Position

def clone_viewresults(viewresults):
    """ Clone a viewresults objects so we don't use its cache"""
    #TODO  move this to couchdbkit
    clone = viewresults.__class__(viewresults.view, **viewresults.params)
    return clone

def documents_list(request, queryset, template_name='index.html', template_object_name='object_list', order_by=None):
    #TODO  move this to couchdbkit
    queryset = clone_viewresults(queryset)
    if order_by:
        sort_reverse = False
        if order_by[0] == '-':
            sort_reverse = True
            order_by = order_by[1:]

        sort_func = lambda x: getattr(x, order_by)

        queryset = queryset.all()
        queryset.sort(key=sort_func, reverse=sort_reverse)

    context = {
        template_object_name : queryset,
    }

    return direct_to_template(request, template_name, context)

# TODO : Not really happy with key_queryset,but that will probably take some more refactoring in the views
def documents_list_per_key(request, queryset, key_queryset, template_name='index.html', template_object_name='object', template_key_name='key', sort_func=None, sort_reverse=False):
    if sort_func:
        queryset = queryset.all()
        queryset.sort(key=sort_func, reverse=sort_reverse)

    context = {
        template_object_name : queryset,
        template_key_name: key_queryset.first()['value'],
    }

    return direct_to_template(request, template_name, context)

def index_by_country(request, country_code):
    sort_func = lambda mep: mep['last']
    query = MEP.view('meps/by_country', key=country_code)
    key_query = MEP.view('meps/countries', key=country_code)

    return documents_list_per_key(request, query, key_query, template_object_name='meps', sort_func=sort_func, template_key_name='country')

def index_by_group(request, group):
    sort_func = lambda mep: mep['last']
    query = MEP.view('meps/by_group', key=group)
    key_query = MEP.view('meps/groups', key=group)
    return documents_list_per_key(request, query, key_query, template_object_name='meps', sort_func=sort_func, template_key_name='group', template_name='meps/by_group.html')

def score_to_color(score):
    """
    map a score between 0 and 100 to a red-green colorspace
    """
    red = 255 - score
    green = score * 2.55
    return "rgb(%d, %d, 0)" % (red, green)

def mep(request, mep_id):
    mep_ = MEP.get(mep_id)
    positions = Position.objects.filter(mep_id=mep_id)
    score_list = mep_.scores
    for score in score_list:
        score['color'] = score_to_color(int(score['value']))
    score_list.sort(key = lambda k : datetime.strptime(k['date'], "%d/%m/%Y"))
    scores = [s['value'] for s in mep_.scores]

    if score_list:
        try:
            import numpy
            import matplotlib
            matplotlib.use("Agg")
            from matplotlib import pyplot

            pyplot.plot(scores, 'bo')
            a, b = numpy.polyfit(range(len(scores)), [int(x) for x in scores], 1)
            pyplot.plot([a*int(x) + b for x in range(len(scores))])
            pyplot.legend(('Scores', 'Mediane'), 'best', shadow=True)
            pyplot.plot(scores)
            pyplot.axis([0, len(scores) - 1, 0, 102])
            pyplot.title("%s - Votes notes evolution over time" % (mep_.infos['name']['full']))
            pyplot.xticks(range(len(scores)), [k['date'] for k in score_list])
            pyplot.xlabel("Votes dates")
            pyplot.ylabel("Scores on votes")
            pyplot.savefig(realpath(".%simg/trends/meps/%s-scores.png" % (settings.MEDIA_URL, mep_id)), format="png")
            pyplot.clf()
        except ImportError:
            pass

    context = {
        'mep_id': mep_id,
        'mep': mep_,
        'positions': positions,
        'visible_count': len([x for x in positions if x.visible]),
        'average': sum(scores)/len(scores) if len(scores) > 0 else "",
        'score_list' : score_list,
    }
    return direct_to_template(request, 'meps/mep.html', context)

def mep_json(request, mep_id):
    mep_ = MEP.get(mep_id)
    jsonstr = simplejson.dumps(dict(mep_), indent=4, use_decimal=True)
    return HttpResponse(jsonstr)

def mep_raw(request, mep_id):
    mep_ = MEP.get(mep_id)
    jsonstr = simplejson.dumps(dict(mep_), indent=4, use_decimal=True)
    context = {
        'mep_id': mep_id,
        'mep': mep_,
        'jsonstr': jsonstr,
    }
    return direct_to_template(request, 'meps/mep_raw.html', context)

def mep_addposition(request, mep_id):
    if not request.is_ajax():
        return HttpResponseServerError()
    results = {'success':False}
    # make sure the mep exists
    mep_ = MEP.view('meps/by_id', key=mep_id).first()

    # For testing purpose: add the possibility to cause a failure in the js (if
    # in debug) to see what's would happened for the user
    try:
        text = request.GET.get(u'text', '')
        if settings.DEBUG:
            if 'slow' in text:
                time.sleep(10)
            if 'fail' in text:
                raise Exception("Simulated failure ! (input contains 'fail' and DEBUG is on)")
        pos = Position(mep_id=mep_id, content=text)
        pos.submitter_username = request.user.username
        pos.submitter_ip = request.META["REMOTE_ADDR"]
        pos.submit_datetime = datetime.today()
        pos.moderated = False
        pos.visible = False
        pos.save()
        results = {'success':True}
    except:
        pass
    return HttpResponse(simplejson.dumps(results), mimetype='application/json')

@staff_member_required
def moderation(request):
    positions = Position.objects.filter(moderated=False)
    context = {
        'positions': positions,
    }
    return direct_to_template(request, 'meps/moderation.html', context)

@staff_member_required
def moderation_get_unmoderated_positions(request):
    if not request.is_ajax():
        return HttpResponseServerError()

    last_id = request.GET[u'last_id']
    positions =  Position.objects.filter(moderated=False, id__gt=last_id)
    return HttpResponse(serializers.serialize('json', positions), mimetype='application/json')

@staff_member_required
def moderation_moderate_positions(request):
    if not request.is_ajax():
        return HttpResponseServerError()
    results = {'success':False}
    position = get_object_or_404(Position, pk=int(request.GET[u'pos_id']))
    try:
        position.moderated = True
        position.visible = (request.GET[u'decision'] == "1")
        position.save()
        results = {'success':True}
    except:
        pass
    return HttpResponse(simplejson.dumps(results), mimetype='application/json')

