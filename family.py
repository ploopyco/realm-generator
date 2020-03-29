import math
import random
import copy

from . import person
from .alignment import get_alignment

from .word.name.noble import noble_names
from .word.motto import mottos
from .word.adjective.standard import adjectives
from .word.appointment import appointments, chiefs, councils
from .word.seat import seat_suffixes


ROYAL_FAMILY = "royal"
GREAT_FAMILY = "great"
MINOR_FAMILY = "minor"
PETTY_FAMILY = "petty"


class Family():
    def __init__(self, data, name, rank):
        self.name = name
        self.vassals = []
        self.knights = []
        self.events = []
        self.rank = rank
        self.motto = random.choice(mottos)
        self.reputation = random.choice(adjectives)

        self.alignment, self.alignment_print = get_alignment(data)

        self.family_realm_name = data['realm']['name']
        self.family_realm_plural = data['realm']['plural']

        self.seat = self._generate_seat(data)
        self.persons = self._instantiate_persons(data)
        self.courtiers = self._instantiate_courtiers(data)

    def get_leader(self):
        h = [m for m in self.persons if m.head is True]
        if len(h) > 0:
            return h[0]

    def get_full_name(self):
        if self.rank == ROYAL_FAMILY:
            return "Royal {} of {}".format(self.family_realm_name, self.name)
        elif self.rank == GREAT_FAMILY:
            return "Great {} of {}".format(self.family_realm_name, self.name)
        elif self.rank == MINOR_FAMILY:
            return "Minor {} of {}".format(self.family_realm_name, self.name)
        elif self.rank == PETTY_FAMILY:
            return "Petty {} of {}".format(self.family_realm_name, self.name)

    def get_families_recursive(self, families):
        families.append(self)

        for v in self.vassals:
            v.get_families_recursive(families)

        for k in self.knights:
            k.get_families_recursive(families)

        return families

    def get_persons_recursive(self, persons):
        for p in self.persons:
            persons.append((self, p))

        for v in self.vassals:
            v.get_persons_recursive(persons)

        for k in self.knights:
            k.get_persons_recursive(persons)

        return persons

    def get_courtiers_recursive(self, courtiers):
        for c in self.courtiers:
            courtiers.append(c)

        for v in self.vassals:
            v.get_courtiers_recursive(courtiers)

        for k in self.knights:
            k.get_courtiers_recursive(courtiers)

        return courtiers

    def create_html_a_name(self, families):
        data_family = self.create_link_from_name(self.name, families)

        html = (
            '<a class="family-link" href="#" data-family="{}">'
            '{}</a>'
        ).format(
            data_family,
            self.get_full_name()
        )

        return html

    def create_link_from_name(self, name, families):
        # O(n) operation - don't abuse it!
        for f in families:
            if f.name == name:
                return name
            else:
                rv = self.create_link_from_name(name, f.vassals)
                if rv is not None:
                    return "{}/{}".format(f.name, rv)

                rk = self.create_link_from_name(name, f.knights)
                if rk is not None:
                    return "{}/{}".format(f.name, rk)
        return None

    def _generate_seat(self, data):
        r = random.random()
        if r > 0.3:
            seat = "{} {}".format(
                random.choice(noble_names),
                random.choice(seat_suffixes)
            )
        elif r > 0.2:
            seat = "{} {} {}".format(
                random.choice(noble_names),
                random.choice(seat_suffixes),
                random.choice(seat_suffixes)
            )
        elif r > 0.1:
            seat = "{} {}".format(
                random.choice(adjectives).capitalize(),
                random.choice(seat_suffixes)
            )
        else:
            seat = "{} {}".format(
                random.choice(data['animals']),
                random.choice(seat_suffixes)
            )

        return seat

    def _instantiate_persons(self, data):
        persons = []

        leader = person.Noble(
            data,
            self.name,
            self.rank,
            alignment=self.alignment,
            leader=True
        )
        persons.append(leader)

        if random.random() > 0.2:
            spouse = person.Noble(
                data,
                self.name,
                self.rank,
                alignment=self.alignment,
                race=leader.race,
                max_age=leader.age,
            )
            spouse.set_spouse(data, leader)
            persons.append(spouse)

        if leader.age < 30:
            num_of_fam = math.floor(random.random() * 2)
        elif leader.age < 50:
            num_of_fam = math.floor(random.random() * 7)
        else:
            num_of_fam = math.floor(random.random() * 11)

        for _ in range(num_of_fam):
            mem = person.Noble(
                data,
                self.name,
                self.rank,
                alignment=self.alignment,
                race=leader.race,
                max_age=leader.age,
            )

            if mem.age == 0:
                continue
            else:
                persons.append(mem)

        return persons

    def _instantiate_courtiers(self, data):
        courtiers = []

        if self.rank == ROYAL_FAMILY:
            num = 10 + math.floor(random.random() * 21)
        elif self.rank == GREAT_FAMILY:
            num = 4 + math.floor(random.random() * 19)
        elif self.rank == MINOR_FAMILY:
            num = 1 + math.floor(random.random() * 11)
        elif self.rank == PETTY_FAMILY:
            num = math.floor(random.random() * 4)

        for _ in range(num):
            courtier = person.Person(data)
            courtier.age = max(courtier.age, person.ADULT_AGE)
            if random.random() > 0.5:
                courtier.position = random.choice(appointments)
            else:
                courtier.position = "{} of {}".format(
                    random.choice(chiefs).capitalize(),
                    random.choice(councils)
                )
            courtiers.append(courtier)

        return courtiers


def create_nobility(
    data,
    great_houses,
    minor_houses,
    landed_knights
):

    nobility = []

    noble_names_cp = copy.deepcopy(noble_names)

    royalty = noble_names_cp.pop()
    royal_house = Family(data, royalty, ROYAL_FAMILY)
    nobility.append(royal_house)

    for _ in range(great_houses - 1):
        name = noble_names_cp.pop()
        h = Family(data, name, GREAT_FAMILY)
        nobility.append(h)

    for _ in range(minor_houses):
        name = noble_names_cp.pop()
        h = Family(data, name, MINOR_FAMILY)
        liege = random.choice(nobility)
        liege.vassals.append(h)

    for _ in range(landed_knights):
        name = noble_names_cp.pop()
        h = Family(data, name, PETTY_FAMILY)
        liege = random.choice(nobility)

        if (random.random() > great_houses / (great_houses + minor_houses) and
                len(liege.vassals) > 0):
            minor_liege = random.choice(liege.vassals)
            minor_liege.knights.append(h)
        else:
            liege.knights.append(h)

    return nobility


def all_families(nobility):
    families = []
    for gh in nobility:
        gh.get_families_recursive(families)
    return families


def random_family(nobility):
    families = all_families(nobility)
    return random.choice(families)


def all_nobles(nobility):
    nobles = []
    for gh in nobility:
        gh.get_persons_recursive(nobles)
    return nobles


def random_noble(nobility):
    nobles = all_nobles(nobility)
    return random.choice(nobles)


def all_courtiers(nobility):
    courtiers = []
    for gh in nobility:
        gh.get_courtiers_recursive(courtiers)
    return courtiers


def random_courtier(nobility):
    courtiers = all_courtiers(nobility)
    return random.choice(courtiers)
