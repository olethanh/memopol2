# -*- coding: utf-8 -*-

import os
import sys
from optparse import make_option
from urllib2 import urlopen, URLError

from django.conf import settings
from django.core.management.base import BaseCommand

from couchdbkit import Server, Consumer

from meps.models import MEP

from indexer.models import MEPDescriptor


class Command(BaseCommand):
    help = u'Get latest changes from couchdb and updates the sql index'
    requires_model_validation = False

    option_list = BaseCommand.option_list[1:] + (
        make_option('-v', '--verbosity', action='store', dest='verbosity', default='4',
            type='choice', choices=map(str, range(5)),
            help='Verbosity level; 0=no output, 1=only dots, 2=only scenario names, 3=colorless output, 4=normal output (colorful)'),

        make_option('-a', '--apps', action='store', dest='apps', default='',
            help='Run ONLY the django apps that are listed here. Comma separated'),

        make_option('-A', '--avoid-apps', action='store', dest='avoid_apps', default='',
            help='AVOID running the django apps that are listed here. Comma separated'),

        make_option('-S', '--no-server', action='store_true', dest='no_server', default=False,
            help="will not run django's builtin HTTP server"),

        make_option('-d', '--debug-mode', action='store_true', dest='debug', default=False,
            help="when put together with builtin HTTP server, forces django to run with settings.DEBUG=True"),

    )

    """
    def notify_change(self, db_name, item_id):
        try:
            dest_url = u"http://localhost:8000/list/update/%s/%s/" % (db_name, item_id)
            print dest_url
            urlopen(dest_url).read()
        except URLError:
            pass
    """
    
    def update_index_for_mep(self, mep_id):
        print "mep", mep_id
        mep_ = MEP.get(mep_id)
        desc = MEPDescriptor()
        desc.mep_id = mep_id
        desc.score = 42
        desc.country = mep_["infos"]["constituency"]["country"]["code"]
        desc.gender = mep_["infos"]["gender"]
        try:
            desc.birth_year = int(mep_["infos"]["birth"]["date"]["year"])
        except ValueError:
            pass
        desc.group =  mep_["infos"]["group"]["abbreviation"]
        desc.save()

        
    def update_index_for_mp(self, mp_id):
        #print "mp", mp_id
        pass
    
    def update_index_for_vote(self, vote_id):
        #print "votes", vote_id
        pass
    
    def update_index_for_item(self, db_name, item_id):
        dispatch = {"meps": self.update_index_for_mep, "mps": self.update_index_for_mp, "votes": self.update_index_for_vote}
        dispatch[db_name](item_id)
    
    def handle(self, *args, **options):
        settings.DEBUG = options.get('debug', False)

        verbosity = int(options.get('verbosity', 4))
        apps_to_run = tuple(options.get('apps', '').split(","))
        apps_to_avoid = tuple(options.get('avoid_apps', '').split(","))
        run_server = not options.get('no_server', False)

        failed = False

        try:
            server = Server(settings.COUCHDB)
            for db_name, db_url in settings.COUCHDB_DATABASES:
                db = server[db_name]
                consumer = Consumer(db)
                changes = consumer.fetch()
                for item in changes['results']:
                    item_id = item['id']
                    if item_id[0] != '_':
                        self.update_index_for_item(db_name, item_id)
        except Exception, e:
            import traceback
            traceback.print_exc(e)

        finally:
            pass

