import os
from fabric.api import local
from fabric.context_managers import shell_env


def prepare():
    """"copy database and migrate"""
    from django.conf import settings
    db = settings.DATABASES['default']
    args = '-h {HOST} -U {USER} {NAME}'.format(**db)
    if db['NAME'] != 'ose_production':
        local('dropdb {}'.format(args))
        local('createdb -T ose_production {}'.format(args))
    local('./manage.py migrate --noinput')
    local('psql -c "VACUUM ANALYZE" {}'.format(args))


def uwsgi():
    """start uwsgi service"""
    local("uwsgi"
          " --module=ose.wsgi"
          " --socket=0.0.0.0:80"
          " --static-map /static=/static"
          " --attach-daemon=\"celery -A ose worker -B\""
          " --env DJANGO_SETTINGS_MODULE={}".format(
              os.environ['DJANGO_SETTINGS_MODULE']))


def test():
    """django continuous integration test"""
    with shell_env(DJANGO_SETTINGS_MODULE='ose.settings.test'):
        local('coverage run -p manage.py test -v 2 ose.apps ose.lib')
        local('coverage combine')
        local('coverage html -d reports')


def updatecopyright():
    import glob
    from itertools import chain
    paths = [f for f in chain(
        glob.glob('ose/*.py'),
        glob.glob('ose/apps/**/*.py', recursive=True),
        glob.glob('ose/lib/**/*.py', recursive=True),
    ) if 'migrations' not in f]
    copyright = open('COPYRIGHT').read()
    for file in paths[1:]:
        lines = iter(open(file).readlines())
        line = ''
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                break
        with open(file, 'w') as new:
            new.write(copyright)
            if line:
                new.write(line+'\n')
            new.writelines(lines)


def initialdata():
    import csv
    from datetime import datetime, date, timedelta
    import django; django.setup()
    from ose.apps.user.models import User, Position, UserPosition, Term
    from ose.apps.notebook.models import Entry

    remap_names = {
        'lemofack cédric': 'Cédric Lemofack',
        'cédric lemofack': 'Cédric Lemofack',
        'lemofack cedric': 'Cédric Lemofack',
        'emmanouil karamousadakis': 'Emmanouil Karamousadakis',
        'jean-baptiste vervaeck': 'Jean-Baptiste Vervaeck',
        'marcin': 'Marcin Jakubowski',
        'jose carlos urra': 'Jose Urra',
        'jose carlos urra llanusa': 'Jose Urra',
        'abeanderson': 'Abe Anderson',
        'ayodele  arigbabu': 'Ayodele Arigbabu',
        'chas murillo': 'Charles Murillo',
        'hart': 'Hart Larew',
        'jozef mikler iii': 'Jozef Mikler',
        'laszlolg': 'Laszlo LG',
        'oliver schlüter': 'Oliver Schlueter',
    }
    data = {}
    with open('initial.csv') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            name_col = row[1].strip()
            name = remap_names.get(name_col.lower(), name_col)
            data.setdefault(name, [])
            data[name].append((row[0], float(row[3]), row[2], row[4]))

    remap_users = {
        'Marcin Jakubowski': 'marcin',
        'Jean-Baptiste Vervaeck': 'jbvervaeck',
        'Laszlo LG': 'laszlolg',
        'Lex Berezhny': 'lex'
    }

    osedev = Position.objects.create(name='OSE Developer', weeks=12, description='')
    for name in sorted(data):
        parts = name.split(' ')
        first, last = parts[0], ' '.join(parts[1:])
        username = remap_users.get(name, first[0].lower()+last.lower())

        if username in ['lex', 'marcin', 'jmikler']:
            user = User.objects.create_superuser(username, '', 'password', first_name=first, last_name=last)
        else:
            user = User.objects.create_user(username, '', None, first_name=first, last_name=last)

        for idx, entry in enumerate(data[name]):
            day = datetime.strptime(entry[0], '%m/%d/%Y %H:%M:%S').date()
            Entry.objects.create(
                day=day, user=user, minutes=int(entry[1]*60),
                text='\n'.join(entry[-2:])
            )
            if idx == 0:
                pos = UserPosition.objects.create(user=user, position=osedev)
                pos.term = Term.objects.create(
                    user_position=pos,
                    start=day,
                    end=date.today()+timedelta(days=7*12)
                )
                pos.save()
