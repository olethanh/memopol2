# Create your views here.

from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render_to_response, get_object_or_404
from django.views.generic.simple import direct_to_template

from meps.models import MEP

from models import MEPDescriptor
from forms import QueryForm

def update_mep(request, mep_id):
    """
    called by our couchdb monitoring script to let us know a mep document changed
    """
    mep_ = MEP.get(mep_id)
    desc = MEPDescriptor()
    desc.mep_id = mep_id
    desc.score = 42
    desc.country = mep_["infos"]["constituency"]["country"]["code"]
    desc.gender = mep_["infos"]["gender"]
    desc.birth_year = int(mep_["infos"]["birth"]["date"]["year"])
    desc.group =  mep_["infos"]["group"]["abbreviation"]
    desc.save()
    return HttpResponse('{"success": true}', content_type="application/json")

def update_mp(request, mp_id):
    pass

def update_vote(request, vote_id):
    pass
