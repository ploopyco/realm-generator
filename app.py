import flask
import flask_wtf
import wtforms
import wtforms.validators
import random
import os
import json

from . import family
from . import faction
from . import event

from .word.name.noble import noble_names
from .word.name.female import female_names
from .word.name.male import male_names
from .word.name.nickname import nick_names
from .word.adjective.whimsical import whimsical_adjectives
from .word.adjective.standard import adjectives
from .word.animal import animals
from .word.cognomen import cognomens
from .word.race import races
from .word.motto import mottos
from .word.title import titles
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

    chosen_titles = form.titles.data

    family_realm_name = form.realms.data

    random.shuffle(noble_names)
    random.shuffle(male_names)
    random.shuffle(female_names)
    random.shuffle(cognomens)
    random.shuffle(nick_names)
    random.shuffle(whimsical_adjectives)
    random.shuffle(adjectives)
    random.shuffle(races)
    random.shuffle(animals)
    random.shuffle(mottos)
    random.shuffle(seat_suffixes)

    chosen_titles_d = [d for d in titles if d["type"] == chosen_titles][0]

    nobility = family.create_nobility(
        great_families,
        minor_families,
        knights,
        chosen_titles_d,
        family_realm_name
    )

    factions = faction.create_factions(
        powerful_factions,
        weak_factions,
        nobility
    )

    event_generator = event.EventGenerator(nobility, factions)
    for _ in range(start_noble_events):
        event_generator.new_noble_event()
    for _ in range(start_courtier_events):
        event_generator.new_courtier_event()
    for _ in range(start_family_events):
        event_generator.new_family_event()

    realm = {
        "nobility": nobility,
        "factions": factions
    }

    return json.dumps(realm, cls=RealmEncoder)


class GenerateForm(flask_wtf.FlaskForm):
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
        choices=[
            ('british', 'British (King, Lord, Sir)'),
            ('roman', 'Roman (Emperor, Dominus, Consulus)'),
            ('byzantine', 'Byzantine (Basileus, Despot, Sebastor)'),
            ('russian', 'Russian (Tsar, Count, Baron)'),
            ('sanskrit', 'Sanskrit (Maharaja, Amir, Sardar)'),
            ('persian', 'Persian (Shah, Marzban, Istandar)')
        ],
        default='british'
    )

    realms = wtforms.RadioField(
        'Family Realm Names',
        choices=[
            ('House', 'House (i.e. The Great House of Whatever)'),
            ('Hearth', 'Hearth (i.e. The Great Hearth of Whatever)'),
            ('Domain', 'Domain (i.e. The Great Domain of Whatever)'),
            ('Clan', 'Clan (i.e. The Great Clan of Whatever)'),
            ('Tribe', 'Tribe (i.e. The Great Tribe of Whatever)'),
            ('Dynasty', 'Dynasty (i.e. The Great Dynasty of Whatever)'),
            ('Fastness', 'Fastness (i.e. The Great Fastness of Whatever)')
        ],
        default='House'
    )

    submit = wtforms.SubmitField('Generate A Realm Now!')


class RealmEncoder(json.JSONEncoder):
    def default(self, o):
            return o.__dict__
