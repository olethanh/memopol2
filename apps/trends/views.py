import logging
import os
from os.path import realpath
from datetime import datetime

from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound

from meps.models import MEP

logger = logging.getLogger("trends.view")
try:
    import numpy
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import pyplot
    has_matplotlib = True
except ImportError:
    has_matplotlib = False
    logger.warning("Install matplotlib to have statistics for each MEP")

def send_file(request, filename, content_type='text/plain'):
    """
    Send a file through Django.
    """
    ## Seems to no longer work with recent django
    #wrapper = FileWrapper(open(filename))
    buffer = open(filename, 'rb').read()
    response = HttpResponse(buffer, content_type=content_type)
    response['Content-Length'] = os.path.getsize(filename)
    return response

def trends_for_mep(request, mep_id):
    filename = realpath(".%simg/trends/meps/%s-scores.png" % (settings.MEDIA_URL, mep_id))
    force = request.GET.get(u'force', '0')
    force = False if force == '0' else True

    if force or not os.path.exists(filename):
        mep_ = MEP.get(mep_id)
        score_list = mep_.scores
        score_list.sort(key = lambda k : datetime.strptime(k['date'], "%d/%m/%Y"))
        scores = [s['value'] for s in mep_.scores]
        score_dates = [datetime.strptime(k['date'], "%d/%m/%Y") for k in score_list]
        print scores
        print score_dates
        if scores and has_matplotlib:
                pyplot.plot_date(score_dates, scores, 'bo-')
                pyplot.legend(('Scores', 'Mediane'), 'best', shadow=True)
#                pyplot.plot(scores)
#                pyplot.axis([0, len(scores) - 1, 0, 102])
                pyplot.title("%s - Votes notes evolution over time" % (mep_.infos['name']['full']))
#                pyplot.xticks(range(len(scores)), [k['date'] for k in score_list])
                pyplot.xlabel("Votes dates")
                pyplot.ylabel("Scores on votes")
                pyplot.savefig(filename, format="png")
                pyplot.clf()
        else:
                return HttpResponseNotFound

    return send_file(request,filename, content_type="image/png")

def trends_for_meps(request, meps_id):
    print meps_id
    filename = realpath("cache/%s-scores.png" % (meps_id))
    force = request.GET.get(u'force', '0')
    force = False if force == '0' else True

    if not has_matplotlib:
        return False

    meps_id = meps_id.split(",")
    all_dates = set()
    for mep_id in meps_id:
        print mep_id
        mep = MEP.get(mep_id)
        score_list = mep.scores
        score_list.sort(key = lambda k : datetime.strptime(k['date'], "%d/%m/%Y"))
        scores = [s['value'] for s in mep.scores]
        score_dates = [datetime.strptime(k['date'], "%d/%m/%Y") for k in score_list]
        print scores
        print score_dates
        pyplot.plot_date(score_dates, scores, 'bo-')

    pyplot.legend(meps_id, 'best', shadow=True)
    pyplot.title("%s - Votes notes evolution over time" % (mep.infos['name']['full']))
#    pyplot.xticks(range(len(all_dates)), all_dates)
    pyplot.xlabel("Votes dates")
    pyplot.ylabel("Scores on votes")
    pyplot.savefig(filename, format="png")
    pyplot.clf()

    return send_file(request,filename, content_type="image/png")

