# Create your views here.

from django.shortcuts import render_to_response
from django.views.generic.simple import direct_to_template

from meps.models import MEP
from indexer.models import MEPDescriptor
from forms import QueryForm

def query(request):
    form = QueryForm(request.GET)
    if not form.is_valid():
        return render_to_response('query.html')
    key=[]
    #for fltr in ('commitee_filter', 'group_filter', 'country_filter'):
    #    val=form.cleaned_data.get(fltr)
    #    if val: key.append(val)
    key=[form.cleaned_data.get('country_filter') or u'DE',
         form.cleaned_data.get('group_filter') or u'PPE',
         form.cleaned_data.get('commitee_filter',None)]
    print key
    meps = MEP.view('meps/query', key=key)
    return render_to_response('queries/query.html', { 'meps': meps})

def indexquery(request):
    form = QueryForm(request.GET)
    if not form.is_valid():
        return render_to_response('queries/iquery.html')
    options = {}
    country = form.cleaned_data.get('country_filter', None)
    group = form.cleaned_data.get('group_filter', None)
    if country:
        options['country'] = country
    if group:
        options['group'] = group
    meps = MEPDescriptor.objects.filter(**options)
    return render_to_response('queries/iquery.html', { 'meps': meps})
