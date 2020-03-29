import flask
import flask_wtf
import wtforms
import wtforms.validators
import random
import os
import json
import glob

from . import family
from . import faction
from . import event

from .word.name.noble import noble_names
from .word.name.female import female_names
from .word.name.male import male_names
from .word.name.nickname import nick_names
from .word.adjective.whimsical import whimsical_adjectives
from .word.adjective.standard import adjectives
from .word.cognomen import cognomens
from .word.motto import mottos
from .word.seat import seat_suffixes

# Some good default values
GREAT_FAMILIES = 7
MINOR_FAMILIES = 45
LANDED_FAMILIES = 350
POWERFUL_FACTIONS = 7
WEAK_FACTIONS = 19
START_NOBLE_EVENTS = 500
START_COURTIER_EVENTS = 500
START_FAMILY_EVENTS = 250

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)


@app.route('/', methods=['GET', 'POST'])
def index():
    form = GenerateForm()
    if form.validate_on_submit():
        realm = generate_realm(form)
        return flask.render_template(
            'realm.html',
            realm=realm
        )
    else:
        return flask.render_template(
            'home.html',
            form=form,
            noble_limit=len(noble_names)
        )


@app.route('/load')
def load():
    realm = "null"
    return flask.render_template('realm.html', realm=realm)


@app.route('/donate', methods=['GET', 'POST'])
def dn():
    form = donate.DonateForm()
    if form.validate_on_submit():
        link = donate.process_form(form)
        return flask.redirect(link)
    else:
        return flask.render_template('donate.html', form=form)


def generate_realm(form):
    great_families = form.great_families.data
    minor_families = form.minor_families.data
    knights = form.knights.data

    powerful_factions = form.powerful_factions.data
    weak_factions = form.weak_factions.data

    start_noble_events = form.start_noble_events.data
    start_courtier_events = form.start_courtier_events.data
    start_family_events = form.start_family_events.data

    data = {
        'races' : [],
        'titles' : {},
        'realm' : {},
        'alignment' : {},
        'animals' : []
        }

    jsonfiles = glob.glob("word/*.json")

    for f in jsonfiles:
        with open(f) as jfile:
            obj = json.load(jfile)
            for d in obj['data']:
                if d['type'] == 'races' and d['id'] in form.races.data:
                    data['races'].extend(d['list'])
                elif d['type'] == 'titles' and d['id'] in form.titles.data:
                    data['titles'] = d
                elif d['type'] == 'realm' and d['id'] in form.realms.data:
                    data['realm'] = d
                elif d['type'] == 'alignment' and d['id'] in form.align.data:
                    data['alignment'] = d
                elif d['type'] == 'animals':
                    data['animals'].extend(d['list'])

    data['races'] = list(set(data['races']))
    data['animals'] = list(set(data['animals']))
    
    random.shuffle(noble_names)
    random.shuffle(male_names)
    random.shuffle(female_names)
    random.shuffle(cognomens)
    random.shuffle(nick_names)
    random.shuffle(whimsical_adjectives)
    random.shuffle(adjectives)
    random.shuffle(mottos)
    random.shuffle(seat_suffixes)

    nobility = family.create_nobility(
        data,
        great_families,
        minor_families,
        knights
    )

    factions = faction.create_factions(
        data,
        powerful_factions,
        weak_factions,
        nobility
    )

    event_generator = event.EventGenerator(nobility, factions)
    for _ in range(start_noble_events):
        event_generator.new_noble_event(data)
    for _ in range(start_courtier_events):
        event_generator.new_courtier_event(data)
    for _ in range(start_family_events):
        event_generator.new_family_event(data)

    realm = {
        "nobility": nobility,
        "factions": factions
    }

    return json.dumps(realm, cls=RealmEncoder)


class GenerateForm(flask_wtf.FlaskForm):

    datasets = []
    dataset_names = []
    race_data = []
    title_data = []
    realm_data = []
    align_data = []
    jsonfiles = glob.glob("word/*.json")

    for f in jsonfiles:
        with open(f) as jfile:
            obj = json.load(jfile)
            if obj['dataset'] in dataset_names:
                for dset in datasets:
                    if dset['dataset'] == obj['dataset']:
                        dset['data'].extend(obj['data'])
            elif 'dataset' in obj:
                datasets.append(obj)
                dataset_names.append(obj['dataset'])

    # separated from load to allow for dynamic list building in future
    for dset in datasets:
        for d in dset['data']:
            if d['type'] == 'races':
                race_data.append(d)
            elif d['type'] == 'titles':
                title_data.append(d)
            elif d['type'] == 'realm':
                realm_data.append(d)
            elif d['type'] == 'alignment':
                align_data.append(d)

    race_choices = []
    race_choices.extend([(s['id'], s['name']) for s in race_data])
    race_choices.sort(key=lambda r: r[1])

    title_choices = []
    title_choices.extend([(s['id'], s['name']) for s in title_data])
    title_choices.sort(key=lambda r: r[1])

    realm_choices = []
    realm_choices.extend([(s['id'], s['desc']) for s in realm_data])
    realm_choices.sort(key=lambda r: r[1])

    align_choices = []
    align_choices.extend([(s['id'], s['name']) for s in align_data])
    align_choices.sort(key=lambda r: r[1])

    great_families = wtforms.IntegerField(
        'Great Noble Families',
        validators=[wtforms.validators.DataRequired()],
        default=GREAT_FAMILIES
    )
    minor_families = wtforms.IntegerField(
        'Minor Noble Families',
        validators=[wtforms.validators.DataRequired()],
        default=MINOR_FAMILIES
    )
    knights = wtforms.IntegerField(
        'Landed Knight Families',
        validators=[wtforms.validators.DataRequired()],
        default=LANDED_FAMILIES
    )

    powerful_factions = wtforms.IntegerField(
        'Powerful Factions',
        validators=[wtforms.validators.DataRequired()],
        default=POWERFUL_FACTIONS
    )
    weak_factions = wtforms.IntegerField(
        'Weak Factions',
        validators=[wtforms.validators.DataRequired()],
        default=WEAK_FACTIONS
    )

    start_noble_events = wtforms.IntegerField(
        'Events for Nobles',
        validators=[wtforms.validators.DataRequired()],
        default=START_NOBLE_EVENTS
    )
    start_courtier_events = wtforms.IntegerField(
        'Events for Courtiers',
        validators=[wtforms.validators.DataRequired()],
        default=START_COURTIER_EVENTS
    )
    start_family_events = wtforms.IntegerField(
        'Events for Noble Families',
        validators=[wtforms.validators.DataRequired()],
        default=START_FAMILY_EVENTS
    )

    titles = wtforms.RadioField(
        'Title Stylings',
        choices=title_choices,
        default=title_choices[0][0]
    )

    realms = wtforms.RadioField(
        'Family Realm Names',
        choices=realm_choices,
        default='house'
    )

    races = wtforms.SelectMultipleField(
        'Races',
        choices=race_choices,
        default=[c[0] for c in race_choices if c[0][:2] == 'dd']
    )

    align = wtforms.RadioField(
        'Alignments',
        choices=align_choices,
        default='none'
    )

    submit = wtforms.SubmitField('Generate A Realm Now!')


class RealmEncoder(json.JSONEncoder):
    def default(self, o):
            return o.__dict__
