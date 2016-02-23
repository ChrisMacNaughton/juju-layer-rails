import pwd
import os
import sys

from subprocess import check_call

from charmhelpers import fetch
from charmhelpers.core.hookenv import (
  status_set,
  log,
  charm_dir,
  config,
  open_port,
  unit_public_ip,
)

from charmhelpers.core.host import (
    adduser,
    service_restart,
    service_running,
    service_start,
)

from charmhelpers.core.templating import render
from charms.reactive import when, when_not, hook
from charms.reactive import is_state, set_state, remove_state
from rubylib import bundle, gem, ruby_dist_dir


@hook('install')
def install():
    if is_state('app.installed'):
        return
    adduser('puma')
    fetch.apt_install(fetch.filter_installed_packages(['git', 'libpq-dev', 'nodejs']))
    
    if config('deploy_key') is not None:
        render(
            source='key',
            target='/root/.ssh/id_rsa',
            perms=0o600,
            context={
              'key': config('deploy_key')
            }
        )

    install_site()

    domain = config('domain')
    if domain is None or domain == '':
        domain = unit_public_ip()
    render(source='puma.conf',
           target='/etc/init/puma.conf',
           owner='root',
           group='root',
           perms=0o644,
           context={
            'workers': config('web_workers'),
            'threads': config('worker_threads'),
            'app_path': config('app-path'),
            'secret_key_base': config('secret_key_base'),
            'domain': domain,
        })
    render(source='nginx.conf',
           target='/etc/nginx/sites-enabled/puma.conf',
           owner='root',
           group='root',
           perms=0o644,
           context={
            'port': config('web_port'),
            'app_path': config('app-path'),
        })
    open_port(config('web_port'))
    
    if service_running('nginx'):
        service_restart('nginx')
    else:
        service_start('nginx')
    chown(config('app-path'), 'puma')
    status_set('maintenance', '')
    set_state('app.installed')


def install_site():
    clone()
    if config('commit') is not None:
        update_to_commit()
    chown(config('app-path'), 'puma')

def git():
    return 'GIT_SSH={} git'.format('{}/files/wrap_ssh.sh'.format(charm_dir()))


def clone():
    cmd =  "{} clone {} {}".format(git(), config('repo'), config('app-path'))
    res = check_call(cmd, shell=True)
    if res != 0:
      status_set('error', 'has a problem with git, try `resolved --retry')
      sys.exit(1)
    chown(config('app-path'), 'puma')


def update_to_commit():
    cmd = "cd {} && {} checkout {}".format(config('app-path'), git(), config('commit'))
    res = check_call(cmd, shell=True)
    if res != 0:
      status_set('error', 'has a problem with git, try `resolved --retry')
      sys.exit(1)
    chown(config('app-path'), 'puma')


def chown(path, user):
    uid = pwd.getpwnam(user).pw_uid
    # os.chown(config('app-path'), 'puma', -1)
    for root, dirs, files in os.walk(path):  
      for momo in dirs:  
        os.chown(os.path.join(root, momo), uid, -1)
      for momo in files:
        os.chown(os.path.join(root, momo), uid, -1)


@when('app.ready')
@when_not('db.configured')
def missing_db():
    status_set('blocked', 'Please add relation to a database (PostgreSQL / MySQL)')


@when_not('app.ready')
@when('app.installed', 'ruby.available')
def install_deps():
    bundle('install --without development test --deployment')
    status_set('maintenance', '')
    set_state('app.ready')


@when_not('app.configured')
@when('app.ready', 'db.configured')
def setup_db():
    status_set('maintenance', 'Migrating Database')
    migrate_db()
    status_set('maintenance', '')
    set_state('app.configured')


def migrate_db():
    bundle('exec rake db:migrate')


@when_not('app.running')
@when('app.configured')
def start_app():
    bundle('exec rake assets:precompile')
    # start()
    if os.path.isfile('/etc/nginx/sites-enabled/default'):
      os.remove('/etc/nginx/sites-enabled/default')
    status_set('active', '')
    set_state('app.restart')


@when('app.restart')
def start():
    if service_running('puma'):
        service_restart('puma')
    else:
        service_start('puma')
    if service_running('nginx'):
        service_restart('nginx')
    else:
        service_start('nginx')
    chown(config('app-path'), 'puma')
    set_state('app.running')
    remove_state('app.restart')


@when_not('website.configured')
@when('website.available')
def configure_website(website):
    website.configure(port=config('web_port'))
    set_state('website.configured')


@hook('postgres-relation-joined')
def request_db(pgsql):
    if config('database_name'):
        pgsql.change_database_name(config('database_name'))
        # pgsql.request_roles('juju_ceph-dash')

@when_not('db.configured')
@when('postgres.database.available', 'app.ready')
def setup_postgres_config(psql):
    render(
      source='database.yml', 
      target='{}/config/database.yml'.format(config('app-path')),
      context={
        'type': 'postgresql',
        'db': psql
      }
    )
    chown(config('app-path'), 'puma')
    set_state('db.configured') 
