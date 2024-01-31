import random

from realm_generator import family
from realm_generator import person


MAX_ACTOR_ATTEMPTS = 1000
MAX_GROUP_ATTEMPTS = 1000

class EventGenerator():
    def __init__(self, data, nobility, factions):
        self.nobility = nobility
        self.factions = factions
        self.all_families = family.all_families(nobility)
        self.all_nobles = family.all_nobles(nobility)
        self.all_courtiers = family.all_courtiers(nobility)
        self.noble_event_defs = []
        self.noble_event_weights = []
        self.courtier_event_defs = []
        self.courtier_event_weights = []
        self.family_event_defs = []
        self.family_event_weights = []

        for e_def in data['event_defs']:
            if e_def['event_type'] == 'noble':
                self.noble_event_defs.append(e_def)
                self.noble_event_weights.append(e_def['weight'])
            elif e_def['event_type'] == 'courtier':
                self.courtier_event_defs.append(e_def)
                self.courtier_event_weights.append(e_def['weight'])
            elif e_def['event_type'] == 'family':
                self.family_event_defs.append(e_def)
                self.family_event_weights.append(e_def['weight'])

    def new_noble_event(self, data):
        event_def = random.choices(self.noble_event_defs, weights=self.noble_event_weights)
        return self._new_event(data, event_def[0])

    def new_courtier_event(self, data):
        event_def = random.choices(self.courtier_event_defs, weights=self.courtier_event_weights)
        return self._new_event(data, event_def[0])

    def new_family_event(self, data):
        event_def = random.choices(self.family_event_defs, weights=self.family_event_weights)
        return self._new_event(data, event_def[0])

    def _new_event(self, data, event_def):
        event = Event(data)
        actors = {}
        desc_list = []
        tokens = event_def['description'].split('|')
        group_attempts = MAX_GROUP_ATTEMPTS
        matching = False
        # get all actors defined in event definition
        while not matching and group_attempts > 0:
            group_attempts -= 1
            for actor_def in event_def['actor_defs']:
                if actor_def['type'] == 'family':
                    family = self.get_family_for_event(actor_def)
                    if family is None:
                        return None
                    else:
                        actors.update(family)
                elif actor_def['type'] == 'noble':
                    noble = self.get_noble_for_event(actor_def)
                    if noble is None:
                        return None
                    else:
                        actors.update(noble)
                elif actor_def['type'] == 'courtier':
                    courtier = self.get_courtier_for_event(actor_def)
                    if courtier is None:
                        return None
                    else:
                        actors.update(courtier)
            matching = self.match_reqs(actors, event_def)
        if group_attempts == 0:
            return None
        # build description using defined description and actors
        # first pass to replace random tokens
        if 'random_tokens' in event_def.keys():
            converted = []
            for token in tokens:
                if token in event_def['random_tokens'].keys():
                    token = random.choice(event_def['random_tokens'][token])
                converted.append(token)
            tokens = converted
        # build description by substituting actor names for tokens
        for token in tokens:
            if token in actors.keys():
                if actors[token]['type'] == 'family':
                    desc_list.append(actors[token]['object'].create_html_a_name(self.nobility))
                elif actors[token]['type'] == 'noble':
                    desc_list.append(actors[token]['object'].get_full_title())
                elif actors[token]['type'] == 'courtier':
                    desc_list.append(actors[token]['object'].get_first_name())
                elif actors[token]['type'] == 'c_position':
                    desc_list.append(actors[token]['position'])
            elif token == 'faction':
                desc_list.append(random.choice(self.factions).name)
            elif token == 'animal':
                desc_list.append(random.choice(data['animals']).lower())
            elif token == 'adjective':
                desc_list.append(random.choice(data['adjectives']))
            else:
                desc_list.append(token)
        event.description = "".join(desc_list)
        # attach event to appropriate persons/families
        for var in event_def['attach_event']:
            if (actors[var]['type'] == 'family'
                    or actors[var]['type'] == 'noble' 
                    or actors[var]['type'] == 'courtier'):
                actors[var]['object'].events.append(event)
        return event

    def is_suitable(self, entity, actor_def):
        suitable = True
        e_dict = vars(entity)
        if 'req_eq' in actor_def.keys():
            if not e_dict.items() >= actor_def['req_eq'].items():
                suitable = False
        if 'req_not_eq' in actor_def.keys():
            if e_dict.items() >= actor_def['req_not_eq'].items():
                suitable = False
        if 'req_gt' in actor_def.keys():
            for k, v in actor_def['req_gt'].items():
                if k not in e_dict.keys() or e_dict[k] <= v:
                    suitable = False
        if 'req_lt' in actor_def.keys():
            for k, v in actor_def['req_lt'].items():
                if k not in e_dict.keys() or e_dict[k] >= v:
                    suitable = False
        if 'req_in' in actor_def.keys():
            for k, v in actor_def['req_in'].items():
                if k not in e_dict.keys() or e_dict[k] not in v:
                    suitable = False
        if 'req_not_in' in actor_def.keys():
            for k, v in actor_def['req_not_in'].items():
                if k in e_dict.keys() and e_dict[k] in v:
                    suitable = False
        if 'req_has' in actor_def.keys():
            for k in actor_def['req_has']:
                if k not in e_dict.keys() or e_dict[k] is None:
                    suitable = False
        if 'req_not_has' in actor_def.keys():
            for k in actor_def['req_not_has']:
                if k in e_dict.keys() and e_dict[k] is not None:
                    suitable = False
        if 'req_len_gt' in actor_def.keys():
            for k, v in actor_def['req_len_gt'].items():
                if k not in e_dict.keys() or len(e_dict[k]) <= v:
                    suitable = False
        if 'req_len_lt' in actor_def.keys():
            for k, v in actor_def['req_len_lt'].items():
                if k not in e_dict.keys() or len(e_dict[k]) >= v:
                    suitable = False
        return suitable

    def match_reqs(self, actors, event_def):
        suitable = True
        entities = []
        if actors == {} or 'req_matches' not in event_def.keys():
            return True
        for match in event_def['req_matches']:
            if len(match['actors']) < 2:
                break
            entities = [ v['object'] for k, v in actors.items() if k in match['actors']]
            if 'req_actors_any_eq' in match.keys():
                suitable = False
                e = entities.pop()
                e_dict = vars(e)
                for attr in match['req_actors_any_eq']:
                    for a in entities:
                        a_dict = vars(a)
                        if attr in a_dict.keys() and a_dict[attr] == e_dict[attr]:
                            suitable = True
                            break
                entities.append(e)
            if 'req_actors_any_neq' in match.keys():
                suitable = False
                e = entities.pop()
                e_dict = vars(e)
                for attr in match['req_actors_any_neq']:
                    for a in entities:
                        a_dict = vars(a)
                        if attr in a_dict.keys() and a_dict[attr] != e_dict[attr]:
                            suitable = True
                            break
                entities.append(e)
            if 'req_actors_all_eq' in match.keys():
                e = entities.pop()
                e_dict = vars(e)
                for attr in match['req_actors_all_eq']:
                    for a in entities:
                        a_dict = vars(a)
                        if attr in a_dict.keys() and a_dict[attr] != e_dict[attr]:
                            suitable = False
                            break
                entities.append(e)
            if 'req_actors_all_neq' in match.keys():
                e = entities.pop()
                e_dict = vars(e)
                for attr in match['req_actors_all_neq']:
                    for a in entities:
                        a_dict = vars(a)
                        if attr in a_dict.keys() and a_dict[attr] == e_dict[attr] and e_dict[attr] is not None:
                            suitable = False
                            break
                entities.append(e)
            if 'req_vassalage' in match.keys():
                v = actors[match['req_vassalage']['vassal']]['object']
                l = actors[match['req_vassalage']['lord']]['object']
                if v not in l.vassals and v not in l.knights:
                    suitable = False
        return suitable

    def get_family_for_event(self, actor_def):
        suitable = False
        actor_attempts = MAX_ACTOR_ATTEMPTS
        actors = {}
        # add requirement for # courtiers, nobles if not present
        if 'member_defs' in actor_def.keys():
            num_c = len(
                [m for m in actor_def['member_defs'] if m['type'] == 'courtier']
                )
            num_c -= 1
            num_n = len(
                [m for m in actor_def['member_defs'] if m['type'] == 'noble']
                )
            num_n -= 1
            if not 'req_len_gt' in actor_def.keys():
                actor_def['req_len_gt'] = { 
                    'courtiers': num_c, 'persons': num_n 
                    }
            elif (not 'courtiers' in actor_def['req_len_gt'].keys() 
                    or actor_def['req_len_gt']['courtiers'] < num_c):
                actor_def['req_len_gt']['courtiers'] = num_c
            elif (not 'persons' in actor_def['req_len_gt'].keys() 
                    or actor_def['req_len_gt']['persons'] < num_n):
                actor_def['req_len_gt']['persons'] = num_n
        # get a family meeting requirements
        while not suitable and actor_attempts > 0:
            actor_attempts -= 1
            f = random.choice(self.all_families)
            suitable = self.is_suitable(f, actor_def)
        if actor_attempts == 0:
            return None
        # get family members meeting requirements
        if 'member_defs' in actor_def.keys():
            for member_def in actor_def['member_defs']:
                if member_def['type'] == 'noble':
                    n = self.get_noble_for_event(member_def, f)
                    if n is None:
                        return None
                    else:
                        actors.update(n)
                elif member_def['type'] == 'courtier':
                    c = self.get_courtier_for_event(member_def, f)
                    if c is None:
                        return None
                    else:
                        actors.update(c)
        actors[actor_def['var']] = { 'type': 'family', 'object': f }
        return actors

    def get_noble_for_event(self, actor_def, fam=None):
        suitable = False
        actor_attempts = MAX_ACTOR_ATTEMPTS
        actors = {}
        while not suitable and actor_attempts > 0:
            actor_attempts -= 1
            if fam is not None:
                f = fam
                n = random.choice(f.persons)
            else:
                f, n = random.choice(self.all_nobles)
            suitable = self.is_suitable(n, actor_def)
        if actor_attempts == 0:
            return None
        actors[actor_def['var']] = { 'type': 'noble', 'object': n }
        if 'family_var' in actor_def.keys():
            actors[actor_def['family_var']] = { 'type': 'family', 'object': f }
        return actors

    def get_courtier_for_event(self, actor_def, fam=None):
        suitable = False
        actor_attempts = MAX_ACTOR_ATTEMPTS
        actors = {}
        while not suitable and actor_attempts > 0:
            actor_attempts -= 1
            if fam is not None:
                f = fam
                c = random.choice(fam.courtiers)
            elif 'family_var' in actor_def.keys():
                f = random.choice(self.all_families)
                timeout = 1000
                while len(f.courtiers < 1):
                    timeout -= 1
                    if timeout == 0:
                        return None
                    f = random.choice(self.all_families)
                c = random.choice(f.courtiers)
            else:
                c = random.choice(self.all_courtiers)
            suitable = self.is_suitable(c, actor_def)
        if actor_attempts == 0:
            return None
        actors[actor_def['var']] = { 'type': 'courtier', 'object': c }
        if 'position_var' in actor_def.keys():
            actors[actor_def['position_var']] = { 'type': 'c_position', 'position': c.position }
        if 'family_var' in actor_def.keys():
            actors[actor_def['family_var']] = { 'type': 'family', 'object': f }
        return actors


class Event():
    def __init__(self, data):
        self.affected_organizations = []
        self.affected_persons = []
        self.description = None
        self.reactions = []

        for _ in range(3):
            self.reactions.append(random.choice(data['adjectives']))
