# -*- coding: utf-8 -*-

import os
import sys
from optparse import make_option
from urllib2 import urlopen, URLError

from django.conf import settings
from django.core.management.base import BaseCommand

from couchdbkit import Server, Consumer

from meps.models import MEP
from couchcfg import couchcfg

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
                couchcfg.remove("indexer-%s-last" % db_name)
                # TODO: empty backing table too
        except Exception, e:
            import traceback
            traceback.print_exc(e)
        finally:
            pass
