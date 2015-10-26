import pwd
import os
from charmhelpers.core.hookenv import status_set, log
from charmhelpers.core.templating import render
from charms.reactive import when, when_not
from charms.reactive import set_state, remove_state


@when('apache.available', 'database.available')
def setup_ceph_dash(influx):
    log("Setting up config {}".format(influx))
    render(source='config.js',
           target='/var/www/ceph_dash/js/config.js',
           owner='www-data',
           perms=0o775,
           context={
               'influx': influx
           })
    set_state('apache.start')
    status_set('maintenance', 'Starting Apache')


@when('apache.started')
def started():
    status_set('active', 'Ready')
