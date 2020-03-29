import math
import random

from . import person
from .alignment import get_alignment

from .word.name.faction import faction_prefixes, faction_suffixes
from .word.adjective.standard import adjectives
from .word.adjective.whimsical import whimsical_adjectives
from .word.name.male import male_names


class Faction():
    def __init__(self, data, nobility, powerful=False):
        self.region = random.choice(nobility)
        if len(self.region.vassals) > 0:
            self.region = random.choice(self.region.vassals).name

        self.name = self._generate_name(data)
        self.events = []
        self.persons = []
        self.powerful = powerful
        self.reputation = random.choice(adjectives)

        self.alignment, self.alignment_print = get_alignment(data)

        num_of_mems = 3 + math.floor(random.random() * 7)

        if self.powerful is True:
            self.size = math.floor(
                random.random() * 1000 +
                random.random() * 100 +
                random.random() * 10 +
                num_of_mems
            )
        else:
            self.size = math.floor(
                random.random() * 100 +
                random.random() * 10 +
                num_of_mems
            )

        self.persons.append(person.Person(data, alignment=self.alignment, leader=True))

        for _ in range(num_of_mems - 1):
            mem = person.Person(data, alignment=self.alignment)
            mem.leader_relation = "follower"
            self.persons.append(mem)

        for m in self.persons:
            if m.age < person.ADULT_AGE:
                m.age = person.ADULT_AGE

    def get_leader(self):
        h = [m for m in self.persons if m.head is True]
        if len(h) > 0:
            return h[0]

    def _generate_name(self, data):
        if random.random() > 0.5:
            r = random.random()
            if r > 0.66:
                name = "{} of the {}".format(
                    random.choice(faction_prefixes),
                    random.choice(data['animals'])
                )
            elif r > 0.33:
                name = "{} of Saint {}".format(
                    random.choice(faction_prefixes),
                    random.choice(male_names)
                )
            else:
                name = "{} of {}".format(
                    random.choice(faction_prefixes),
                    self.region
                )
        else:
            if random.random() > 0.5:
                name = "{} {}".format(
                    self.region,
                    random.choice(faction_suffixes)
                )
            else:
                name = "{} {}".format(
                    random.choice(whimsical_adjectives).capitalize(),
                    random.choice(faction_suffixes)
                )

        return name


def create_factions(data, powerful_factions, weak_factions, nobility):
    factions = []

    for _ in range(powerful_factions):
        f = Faction(data, nobility, powerful=True)
        factions.append(f)

    for _ in range(weak_factions):
        f = Faction(data, nobility)
        factions.append(f)

    return factions


def all_agents(factions):
    agents = []
    for f in factions:
        for m in f.members:
            agents.append(m)
    return agents


def random_agent(factions):
    agents = all_agents(factions)
    return random.choice(agents)
