import random
import inspect

from realm_generator import family
from realm_generator import person


class EventGenerator():
    def __init__(self, nobility, factions):
        self.nobility = nobility
        self.factions = factions

    def new_noble_event(self, data):
        event_fs = inspect.getmembers(
            self,
            predicate=inspect.ismethod
        )
        fs_list = [y for (x, y) in event_fs if x.startswith("gen_event_n_")]
        return self._new_event(data, fs_list)

    def new_courtier_event(self, data):
        event_fs = inspect.getmembers(
            self,
            predicate=inspect.ismethod
        )
        fs_list = [y for (x, y) in event_fs if x.startswith("gen_event_c_")]
        return self._new_event(data, fs_list)

    def new_family_event(self, data):
        event_fs = inspect.getmembers(
            self,
            predicate=inspect.ismethod
        )
        fs_list = [y for (x, y) in event_fs if x.startswith("gen_event_f_")]
        return self._new_event(data, fs_list)

    def _new_event(self, data, fs_list):
        if len(fs_list) == 0:
            return
        event = random.choice(fs_list)(data)
        for o in event.affected_organizations:
            o.events.append(event)
        del event.affected_organizations  # prevent circular reference
        for p in event.affected_persons:
            p.events.append(event)
        del event.affected_persons  # prevent circular reference
        return event

    def gen_event_n_matrimony(self, data):
        event = Event(data)

        nobles = family.all_nobles(self.nobility)
        f1, n1 = random.choice(nobles)
        f2, n2 = random.choice(nobles)

        if random.random() * 100 > 10:
            while (n1.sex == n2.sex or
                    n1.get_full_title() == n2.get_full_title()):
                f2, n2 = random.choice(nobles)
        else:
            while n1.get_full_title() == n2.get_full_title():
                f2, n2 = random.choice(nobles)

        event.affected_persons.append(n1)
        event.affected_persons.append(n2)
        event.affected_organizations.append(f1)
        event.affected_organizations.append(f2)

        event.description = "{} of the {} was wed to {} of the {}".format(
            n1.get_full_title(),
            f1.create_html_a_name(self.nobility),
            n2.get_full_title(),
            f2.create_html_a_name(self.nobility)
        )

        return event

    def gen_event_n_divorce(self, data):
        event = Event(data)

        nobles = family.all_nobles(self.nobility)
        f1, n1 = random.choice(nobles)
        f2, n2 = random.choice(nobles)

        if random.random() * 100 > 3.5:
            while (n1.sex == n2.sex or
                    n1.get_full_title() == n2.get_full_title()):
                f2, n2 = random.choice(nobles)
        else:
            while n1.get_full_title() == n2.get_full_title():
                f2, n2 = random.choice(nobles)

        event.affected_persons.append(n1)
        event.affected_persons.append(n2)
        event.affected_organizations.append(f1)
        event.affected_organizations.append(f2)

        event.description = (
            "{} of the {} and {} of the {} officially divorced"
        ).format(
            n1.get_full_title(),
            f1.create_html_a_name(self.nobility),
            n2.get_full_title(),
            f2.create_html_a_name(self.nobility)
        )

        return event

    def gen_event_n_illicit_lovers(self, data):
        event = Event(data)

        nobles = family.all_nobles(self.nobility)
        f1, n1 = random.choice(nobles)
        f2, n2 = random.choice(nobles)

        if random.random() * 100 > 3.5:
            while (n1.sex == n2.sex or
                    n1.get_full_title() == n2.get_full_title()):
                f2, n2 = random.choice(nobles)
        else:
            while n1.get_full_title() == n2.get_full_title():
                f2, n2 = random.choice(nobles)

        event.affected_persons.append(n1)
        event.affected_persons.append(n2)
        event.affected_organizations.append(f1)
        event.affected_organizations.append(f2)

        event.description = (
            "An illicit love affair was discovered "
            "between {} of the {} and {} of the {}".format(
                n1.get_full_title(),
                f1.create_html_a_name(self.nobility),
                n2.get_full_title(),
                f2.create_html_a_name(self.nobility)
            )
        )

        return event

    def gen_event_n_baby(self, data):
        event = Event(data)
        _, n = family.random_noble(self.nobility)
        event.affected_persons.append(n)
        event.description = (
            "A baby was born to {}".format(
                n.get_full_title()
            )
        )
        return event

    def gen_event_n_bastard(self, data):
        event = Event(data)
        _, n = family.random_noble(self.nobility)
        event.affected_persons.append(n)
        event.description = (
            "A bastard was born to {}".format(
                n.get_full_title()
            )
        )
        return event

    def gen_event_n_murdered_commoner(self, data):
        event = Event(data)
        _, n = family.random_noble(self.nobility)
        event.affected_persons.append(n)
        event.description = (
            "{} was strongly suspected in the murder of a commoner".format(
                n.get_full_title()
            )
        )
        return event

    def gen_event_n_tournament_win(self, data):
        event = Event(data)
        _, n = family.random_noble(self.nobility)
        event.affected_persons.append(n)
        event.description = (
            "{} won a regional tournament".format(
                n.get_full_title()
            )
        )
        return event

    def gen_event_n_joined_faction(self, data):
        event = Event(data)
        _, n = family.random_noble(self.nobility)
        f = random.choice(self.factions)
        event.affected_persons.append(n)
        event.description = (
            "{} abdicated and joined the {}".format(
                n.get_full_title(),
                f.name
            )
        )
        return event

    def gen_event_n_celebrated_birthday(self, data):
        event = Event(data)
        _, n = family.random_noble(self.nobility)
        event.affected_persons.append(n)
        event.description = (
            "{} celebrated a birthday".format(
                n.get_full_title()
            )
        )
        return event

    def gen_event_n_dismissed_courtiers(self, data):
        event = Event(data)
        f, n = family.random_noble(self.nobility)
        event.affected_persons.append(n)
        event.description = (
            "{} dismissed all of the courtiers at the {}".format(
                n.get_full_title(),
                f.get_full_name()
            )
        )
        return event

    def gen_event_n_honour_duel(self, data):
        event = Event(data)

        nobles = family.all_nobles(self.nobility)
        f1, n1 = random.choice(nobles)
        f2, n2 = random.choice(nobles)

        while (n1.age < person.ADULT_AGE or n2.age < person.ADULT_AGE or
                n1.get_full_title() == n2.get_full_title()):
            f1, n1 = random.choice(nobles)
            f2, n2 = random.choice(nobles)

        event.affected_persons.append(n1)
        event.affected_persons.append(n2)

        event.description = (
            "{} of the {} dueled with {} of the {}; {} won".format(
                n1.get_full_title(),
                f1.create_html_a_name(self.nobility),
                n2.get_full_title(),
                f2.create_html_a_name(self.nobility),
                random.choice([n1, n2]).get_first_name()
            )
        )

        return event

    def gen_event_n_revenge_killing(self, data):
        event = Event(data)

        nobles = family.all_nobles(self.nobility)
        f1, n1 = random.choice(nobles)
        f2, n2 = random.choice(nobles)

        while (n1.age < person.ADULT_AGE or n2.age < person.ADULT_AGE or
                n1.get_full_title() == n2.get_full_title()):
            f1, n1 = random.choice(nobles)
            f2, n2 = random.choice(nobles)

        event.affected_persons.append(n1)
        event.affected_persons.append(n2)

        event.description = (
            "{} of the {} killed {} of the {} in vengeance".format(
                n1.get_full_title(),
                f1.create_html_a_name(self.nobility),
                n2.get_full_title(),
                f2.create_html_a_name(self.nobility)
            )
        )

        return event

    def gen_event_n_death_illness(self, data):
        event = Event(data)
        _, n = family.random_noble(self.nobility)
        event.affected_persons.append(n)
        event.description = (
            "{} died due to an illness".format(
                n.get_full_title()
            )
        )
        return event

    def gen_event_n_death_commoner(self, data):
        event = Event(data)
        _, n = family.random_noble(self.nobility)
        event.affected_persons.append(n)
        event.description = (
            "{} was killed by a group of commoners".format(
                n.get_full_title()
            )
        )
        return event

    def gen_event_f_claim_pressed(self, data):
        event = Event(data)

        f1 = family.random_family(self.nobility)
        f2 = family.random_family(self.nobility)

        while f1.name == f2.name:
            f2 = family.random_family(self.nobility)

        event.affected_organizations.append(f1)
        event.affected_organizations.append(f2)

        event.description = (
            "The {} has pressed a claim on the {}".format(
                f1.create_html_a_name(self.nobility),
                f2.create_html_a_name(self.nobility)
            )
        )

        return event

    def gen_event_f_uprising(self, data):
        event = Event(data)
        f = family.random_family(self.nobility)
        event.affected_organizations.append(f)
        event.description = (
            "An uprising of smallfolk has taken hold against the {}".format(
                f.get_full_name()
            )
        )
        return event

    def gen_event_f_new_knight(self, data):
        event = Event(data)
        f = family.random_family(self.nobility)
        while f.rank == family.PETTY_FAMILY:
            f = family.random_family(self.nobility)
        event.affected_organizations.append(f)
        event.description = (
            "The {} knighted a new person".format(
                f.get_full_name()
            )
        )
        return event

    def gen_event_f_rebellion(self, data):
        event = Event(data)
        f = family.random_family(self.nobility)
        while f.rank == family.PETTY_FAMILY or len(f.vassals + f.knights) == 0:
            f = family.random_family(self.nobility)
        fv = random.choice(f.vassals + f.knights)
        event.affected_organizations.append(f)
        event.affected_organizations.append(fv)
        event.description = (
            "The {} has rebelled against the {}".format(
                fv.create_html_a_name(self.nobility),
                f.create_html_a_name(self.nobility)
            )
        )
        return event

    def gen_event_f_festival(self, data):
        event = Event(data)
        h = family.random_family(self.nobility)
        event.affected_organizations.append(h)
        event.description = (
            "The {} hosted a festival in honour of {}s".format(
                h.get_full_name(),
                random.choice(data['animals']).lower()
            )
        )
        return event

    def gen_event_f_famine(self, data):
        event = Event(data)
        f = family.random_family(self.nobility)
        event.affected_organizations.append(f)
        event.description = (
            "A famine has struck the {}".format(
                f.get_full_name()
            )
        )
        return event

    def gen_event_f_food_plentiful(self, data):
        event = Event(data)
        f = family.random_family(self.nobility)
        event.affected_organizations.append(f)
        event.description = (
            "A fortuitous crop season has graced the {}".format(
                f.get_full_name()
            )
        )
        return event

    def gen_event_f_drought(self, data):
        event = Event(data)
        f = family.random_family(self.nobility)
        event.affected_organizations.append(f)
        event.description = (
            "A drought has struck the {}".format(
                f.get_full_name()
            )
        )
        return event

    def gen_event_f_water_plentiful(self, data):
        event = Event(data)
        f = family.random_family(self.nobility)
        event.affected_organizations.append(f)
        event.description = (
            "Plentiful rains grace the {}".format(
                f.get_full_name()
            )
        )
        return event

    def gen_event_f_economic_downturn(self, data):
        event = Event(data)
        f = family.random_family(self.nobility)
        event.affected_organizations.append(f)
        event.description = (
            "An economic downturn has struck the {}".format(
                f.get_full_name()
            )
        )
        return event

    def gen_event_f_economic_upturn(self, data):
        event = Event(data)
        f = family.random_family(self.nobility)
        event.affected_organizations.append(f)
        event.description = (
            "An economic upturn has graced the {}".format(
                f.get_full_name()
            )
        )
        return event

    def gen_event_c_implication(self, data):
        event = Event(data)

        f = family.random_family(self.nobility)
        while len(f.courtiers) < 2:
            f = family.random_family(self.nobility)

        c1 = random.choice(f.courtiers)
        c2 = random.choice(f.courtiers)

        while c1.get_first_name() == c2.get_first_name():
            c2 = random.choice(f.courtiers)

        event.affected_persons.append(c1)
        event.affected_persons.append(c2)

        event.description = (
            "{} ({}) was implicated by {} ({}) "
            "in a plot to grab power".format(
                c1.get_first_name(),
                c1.position,
                c2.get_first_name(),
                c2.position
            )
        )

        return event

    def gen_event_c_theft(self, data):
        event = Event(data)

        f = family.random_family(self.nobility)
        while len(f.courtiers) < 2:
            f = family.random_family(self.nobility)

        c1 = random.choice(f.courtiers)
        c2 = random.choice(f.courtiers)

        while c1.get_first_name() == c2.get_first_name():
            c2 = random.choice(f.courtiers)

        event.affected_persons.append(c1)
        event.affected_persons.append(c2)

        event.description = (
            "{} ({}) and {} ({}) were "
            "caught in a plot to steal crown monies".format(
                c1.get_first_name(),
                c1.position,
                c2.get_first_name(),
                c2.position
            )
        )

        return event

    def gen_event_c_office_swap(self, data):
        event = Event(data)

        f = family.random_family(self.nobility)
        while len(f.courtiers) < 2:
            f = family.random_family(self.nobility)

        c1 = random.choice(f.courtiers)
        c2 = random.choice(f.courtiers)
        n = random.choice(f.persons)

        while c1.get_first_name() == c2.get_first_name():
            c2 = random.choice(f.courtiers)

        event.affected_persons.append(c1)
        event.affected_persons.append(c2)

        event.description = (
            "{} ({}) and {} ({}) have swapped offices "
            "by order of {}".format(
                c1.get_first_name(),
                c1.position,
                c2.get_first_name(),
                c2.position,
                n.get_full_title()
            )
        )

        return event

    def gen_event_c_offense(self, data):
        event = Event(data)

        f1, n1 = family.random_noble(self.nobility)
        f2, n2 = family.random_noble(self.nobility)
        while (len(f1.courtiers) < 1 or
                n1.get_full_title() == n2.get_full_title()):
            f1, n1 = family.random_noble(self.nobility)
            f2, n2 = family.random_noble(self.nobility)

        c = random.choice(f1.courtiers)

        event.affected_persons.append(n1)
        event.affected_persons.append(n2)
        event.affected_persons.append(c)

        event.description = (
            "{} ({}) has greatly offended {} of the {}, to the great "
            "consternation of {} of the {}".format(
                c.get_first_name(),
                c.position,
                n2.get_full_title(),
                f2.create_html_a_name(self.nobility),
                n1.get_full_title(),
                f1.create_html_a_name(self.nobility),
            )
        )

        return event

    def gen_event_c_spy(self, data):
        event = Event(data)

        c = family.random_courtier(self.nobility)
        f, n = family.random_noble(self.nobility)

        event.affected_persons.append(c)
        event.affected_persons.append(n)

        event.description = (
            "{} ({}) was revealed to be a spy for {} of the {}".format(
                c.get_first_name(),
                c.position,
                n.get_full_title(),
                f.create_html_a_name(self.nobility)
            )
        )

        return event

    def gen_event_c_duel(self, data):
        event = Event(data)

        c = family.random_courtier(self.nobility)
        f, n = family.random_noble(self.nobility)

        event.affected_persons.append(c)
        event.affected_persons.append(n)

        event.description = (
            "{} ({}) was killed by {} of the {} in a duel of honour".format(
                c.get_first_name(),
                c.position,
                n.get_full_title(),
                f.create_html_a_name(self.nobility)
            )
        )

        return event

    def gen_event_c_hung(self, data):
        event = Event(data)

        f = family.random_family(self.nobility)
        while len(f.courtiers) < 1:
            f = family.random_family(self.nobility)

        c = random.choice(f.courtiers)
        n = random.choice(f.persons)

        event.affected_persons.append(c)
        event.affected_persons.append(n)

        event.description = (
            "{} ({}) was executed by {}".format(
                c.get_first_name(),
                c.position,
                n.get_full_title()
            )
        )

        return event

    def gen_event_c_promotion(self, data):
        event = Event(data)

        f = family.random_family(self.nobility)
        while len(f.courtiers) < 1:
            f = family.random_family(self.nobility)

        c = random.choice(f.courtiers)
        n = random.choice(f.persons)

        event.affected_persons.append(c)
        event.affected_persons.append(n)

        event.description = (
            "{} was promoted to the office of {} by {}".format(
                c.get_first_name(),
                c.position,
                n.get_full_title()
            )
        )

        return event

    def gen_event_c_demotion(self, data):
        event = Event(data)

        f = family.random_family(self.nobility)
        while len(f.courtiers) < 1:
            f = family.random_family(self.nobility)

        c = random.choice(f.courtiers)
        n = random.choice(f.persons)

        event.affected_persons.append(c)
        event.affected_persons.append(n)

        event.description = (
            "{} was removed from the office of {} by {}".format(
                c.get_first_name(),
                c.position,
                n.get_full_title()
            )
        )

        return event


class Event():
    def __init__(self, data):
        self.affected_organizations = []
        self.affected_persons = []
        self.description = None
        self.reactions = []

        for _ in range(3):
            self.reactions.append(random.choice(data['adjectives']))
