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
        if scores and has_matplotlib:
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
                pyplot.savefig(filename, format="png")
                pyplot.clf()
        else:
                return HttpResponseNotFound

    return send_file(request,filename, content_type="image/png")

