# -*- coding: utf-8 -*-

import os
import sys
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand

from couchdbkit import Server, Consumer

from couchcfg import couchcfg
from meps.models import MEP
from indexer.models import MEPDescriptor


class Command(BaseCommand):
    help = u'Get latest changes from couchdb and updates the sql index'
    requires_model_validation = True

    option_list = BaseCommand.option_list[1:] + (
        make_option('-v', '--verbose', action='store_true', dest='verbose', default=False,
            help="Be verbose"),
    )

    def update_index_for_mep(self, mep_id):
        if self.verbose:
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
        self.verbose = options.get('verbose')

        try:
            server = Server(settings.COUCHDB)
            for db_name, db_url in settings.COUCHDB_DATABASES:
                last_seq_seen = couchcfg.get("indexer-%s-last" % db_name, 0)
                db = server[db_name]
                consumer = Consumer(db)
                changes = consumer.fetch(since=last_seq_seen)
                results = changes["results"]
                if not results:
                    if self.verbose:
                        print "no new changes (last seen is %d)" % last_seq_seen
                    continue
                last_seq = changes["last_seq"]
                if self.verbose:
                    print "new changes on db %s (last seen: %d, new: %d)" % (db_name, last_seq_seen, last_seq)
                couchcfg.set("indexer-%s-last" % db_name, last_seq)
                for item in results:
                    item_id = item['id']
                    if item_id[0] != '_':
                        self.update_index_for_item(db_name, item_id)
        except Exception, e:
            import traceback
            traceback.print_exc(e)

        finally:
            pass

