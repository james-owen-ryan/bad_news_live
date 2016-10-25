import random
import jinja2
from paramiko import SSHClient
from scp import SCPClient


PATH_TO_PLAYER_INTERFACE_HTML_FILE = '/Users/jamesryan/Downloads/player_interface.html'
PATH_TO_ACTOR_INTERFACE_HTML_FILE = '/Users/jamesryan/Downloads/actor_interface.html'

ZZZ = open('/Users/jamesryan/Downloads/zzz.txt').readline().capitalize()


class Communicator(object):
    """A helper class that sends mediates communication between the simulation and
    our various game interfaces.
    """

    def __init__(self, game):
        """Initialize a communicator object."""
        self.game = game
        self.player = game.player
        # Attributes corresponding to which logo/icon should be displayed on the
        # player interface at different times
        self.current_logo_src = None
        self.current_logo_height = None
        # Text that is displayed to the player at any given point during gameplay; updated
        # periodically by the gameplay instance
        self.player_exposition = ''
        self.player_exposition_enumeration = ''  # Enumeration of buildings, characters nearby, etc.
        # Special text that may be displayed on the actor interface during gameplay
        self.matches_overview = ''  # Matches to a given query, e.g., 'Found 9 matches'
        self.matches_listing = ''  # Listing of individual matches
        # Special attributes that are set as needed due to computational intensity
        self.interlocutor_source_distribution = []  # What sources fed interlocutor their info about subject
        # Load templates
        template_loader = jinja2.FileSystemLoader(searchpath="./templates")
        template_env = jinja2.Environment(loader=template_loader)
        self.player_template = template_env.get_template('player.html')
        self.actor_template = template_env.get_template('actor.html')

    def update_player_interface(self):
        """Update the player interface by re-writing its HTML file."""
        # Fill in the template
        rendered_player_template = self.player_template.render(communicator=self)
        # Write that out as a local file
        f = open(PATH_TO_PLAYER_INTERFACE_HTML_FILE, 'w')
        f.write(rendered_player_template)
        f.close()
        # SCP that local file so that it is web-facing from my BSOE account
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.connect(hostname='riverdance.soe.ucsc.edu', username='jor', password=ZZZ)
        scp = SCPClient(ssh.get_transport())
        scp.put(PATH_TO_PLAYER_INTERFACE_HTML_FILE, '~/.html/bad_news/player.html')

    def update_actor_interface(self):
        """Update the actor interface by re-writing its HTML file."""
        # Fill in the template
        rendered_actor_template = self.actor_template.render(communicator=self)
        # Write that out as a local file
        f = open(PATH_TO_ACTOR_INTERFACE_HTML_FILE, 'w')
        f.write(rendered_actor_template)
        f.close()
        # SCP that local file so that it is web-facing from my BSOE account
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.connect(hostname='riverdance.soe.ucsc.edu', username='jor', password=ZZZ)
        scp = SCPClient(ssh.get_transport())
        scp.put(PATH_TO_ACTOR_INTERFACE_HTML_FILE, '~/.html/bad_news/actor.html')

    def speak_directly_to_player(self, exposition):
        """Manually edit the player interface and display that text."""
        self.player_exposition = exposition
        self.update_player_interface()

    def test(self):
        """Randomly set an interlocutor and subject of conversation to generate an example actor interface."""
        self.player.interlocutor = random.choice(
            [p for p in self.game.city.residents if
             any(q for q in p.mind.mental_models if q.type == 'person')]
        )
        subject_of_conversation = random.choice(
            [q for q in self.interlocutor.mind.mental_models if q.type == 'person']
        )
        self.player.talk_about(subject_of_conversation)

    def set_sources_of_interlocutor_beliefs_about_subject(self):
        """Set the top sources of interlocutor's beliefs about the subject of conversation."""
        all_sources = []
        all_interlocutor_beliefs_about_subject = [
            f for f in self.interlocutor.all_belief_facets if
            f.subject is self.player.subject_of_conversation
        ]
        for facet in all_interlocutor_beliefs_about_subject:
            for piece in facet.evidence:
                if piece.source:
                    all_sources.append(piece.source)
        source_distribution = []
        for source in set(all_sources):
            percentage_of_my_beliefs_due_to_them = all_sources.count(source)/float(len(all_sources))
            source_distribution.append((source, percentage_of_my_beliefs_due_to_them))
        source_distribution.sort(key=lambda s: s[1], reverse=True)
        self.interlocutor_source_distribution = source_distribution

    def set_player_interface_enumeration_text(self, new_enumeration):
        """Convenience method to change the player-exposition enumeration during an emergency."""
        self.player_exposition_enumeration = new_enumeration
        self.update_player_interface()

    @property
    def interlocutor(self):
        """Return the player's current interlocutor."""
        return self.player.interlocutor

    @property
    def city_name(self):
        """Return the name of the city gameplay is taking place in."""
        return self.game.city.name

    @property
    def current_date(self):
        """Return the name of the city gameplay is taking place in."""
        return self.game.sim.date

    @property
    def interlocutor_location_name(self):
        """Return the address of the interlocutor's location."""
        if self.interlocutor:
            return self.interlocutor.location.name
        else:
            return '-'

    @property
    def interlocutor_location_address(self):
        """Return the address of the interlocutor's location."""
        if self.interlocutor:
            return self.interlocutor.location.address
        else:
            return '-'

    @property
    def interlocutor_full_name(self):
        """Return the interlocutor's full name."""
        if self.interlocutor:
            if self.interlocutor in self.game.next_of_kin:
                return '!' + self.interlocutor.full_name
            else:
                return self.interlocutor.full_name
        else:
            return '-'

    @property
    def interlocutor_age(self):
        """Return the interlocutor's age."""
        if self.interlocutor:
            return str(self.game.player.interlocutor.age)
        else:
            return '-'

    @property
    def interlocutor_purpose_here(self):
        """Return the interlocutor's purpose for being at his or her current location."""
        if self.interlocutor:
            return self.interlocutor.whereabouts.current_occasion
        else:
            return '-'

    @property
    def interlocutor_other_people_here(self):
        """Return the other people at interlocutor's current location, if they're not visible to the player."""
        if self.interlocutor:
            if self.player.outside:  # Talking to someone at their door/buzzer
                if len(self.interlocutor.location.people_here_now) == 1:
                    people_here_now_str = 'None'
                else:
                    people_here_now_str = (
                        ', '.join("{name} ({age})".format(name=p.name, age=p.age) for p in
                                  self.interlocutor.location.people_here_now-{self.interlocutor}
                        )
                    )
            else:
                people_here_now_str = '[Player can see]'
            return people_here_now_str
        else:
            return '-'

    @property
    def interlocutor_openness(self):
        """Return the interlocutor's openness-to-experience string."""
        if self.interlocutor:
            return self.interlocutor.personality.component_str(component_letter='o')
        else:
            return '-'

    @property
    def interlocutor_conscientiousness(self):
        """Return the interlocutor's conscientiousness string."""
        if self.interlocutor:
            return self.interlocutor.personality.component_str(component_letter='c')
        else:
            return '-'

    @property
    def interlocutor_extroversion(self):
        """Return the interlocutor's extroversion string."""
        if self.interlocutor:
            return self.interlocutor.personality.component_str(component_letter='e')
        else:
            return '-'

    @property
    def interlocutor_agreeableness(self):
        """Return the interlocutor's agreeableness string."""
        if self.interlocutor:
            return self.interlocutor.personality.component_str(component_letter='a')
        else:
            return '-'

    @property
    def interlocutor_neuroticism(self):
        """Return the interlocutor's neuroticism string."""
        if self.interlocutor:
            return self.interlocutor.personality.component_str(component_letter='n')
        else:
            return '-'

    @property
    def interlocutor_moved_to_town_when(self):
        """Return when interlocutor moved to town."""
        if self.interlocutor:
            if self.interlocutor.birth and self.interlocutor.birth.city is self.game.city:
                return "birth"
            else:
                return str(self.interlocutor.moves[0].year)
        else:
            return '-'

    @property
    def interlocutor_marital_status(self):
        """Return the interlocutor's marital status."""
        if self.interlocutor:
            if self.interlocutor.spouse:
                return "married ({spouse_name})".format(spouse_name=self.interlocutor.spouse.name)
            else:
                return self.interlocutor.get_feature('marital status')
        else:
            return '-'

    @property
    def interlocutor_home_address(self):
        """Return the interlocutor's home address."""
        if self.interlocutor:
            since_when = ' (since {})'.format(self.interlocutor.moves[-1].year)
            return self.interlocutor.get_feature('home address') + since_when
        else:
            return '-'

    @property
    def interlocutor_job_status(self):
        """Return the interlocutor's job status."""
        if self.interlocutor:
            job_status = self.interlocutor.get_feature('job status')
            if job_status in ('retired', 'unemployed'):
                job_status += ' (since {})'.format(
                    'always' if not self.interlocutor.occupations else
                    self.interlocutor.occupations[-1].terminus.year
                )
            return job_status
        else:
            return '-'

    @property
    def interlocutor_workplace(self):
        """Return the name of the interlocutor's workplace, if any."""
        if self.interlocutor:
            workplace = None if not self.interlocutor.occupations else self.interlocutor.occupations[-1].company
            overview = 'None' if not workplace else workplace.name
            if self.interlocutor.occupation:  # Currently working there
                overview += ' (since {})'.format(self.interlocutor.occupation.start_date)
            if workplace and workplace.out_of_business:
                overview = '[OOB] ' + overview
            return overview
        else:
            return '-'

    @property
    def interlocutor_workplace_address(self):
        """Return the address of the interlocutor's workplace, if any."""
        if self.interlocutor:
            return self.interlocutor.get_feature('workplace address')
        else:
            return '-'

    @property
    def interlocutor_job_title(self):
        """Return the interlocutor's job title, if any."""
        if self.interlocutor:
            return self.interlocutor.get_feature('job title')
        else:
            return '-'

    @property
    def interlocutor_job_shift(self):
        """Return the interlocutor's job shift, if any."""
        if self.interlocutor:
            return self.interlocutor.get_feature('job shift').capitalize()
        else:
            return '-'

    @property
    def interlocutor_skin_color(self):
        """Return the interlocutor's skin color."""
        if self.interlocutor:
            broader_skin_tone = {
                'black': 'dark', 'brown': 'dark',
                'beige': 'light', 'pink': 'light',
                'white': 'light',
            }
            return broader_skin_tone[self.interlocutor.face.skin.color]
        else:
            return '-'

    @property
    def interlocutor_hair_length(self):
        """Return the interlocutor's hair length."""
        if self.interlocutor:
            return self.interlocutor.get_feature('hair length')
        else:
            return '-'

    @property
    def interlocutor_hair_color(self):
        """Return the interlocutor's hair color."""
        if self.interlocutor:
            return self.interlocutor.get_feature('hair color')
        else:
            return '-'

    @property
    def interlocutor_tattoo(self):
        """Return whether the interlocutor has a visible tattoo."""
        if self.interlocutor:
            return self.interlocutor.get_feature('tattoo')
        else:
            return '-'

    @property
    def interlocutor_scar(self):
        """Return whether the interlocutor has a visible scar."""
        if self.interlocutor:
            return self.interlocutor.get_feature('scar')
        else:
            return '-'

    @property
    def interlocutor_birthmark(self):
        """Return whether the interlocutor has a visible birthmark."""
        if self.interlocutor:
            return self.interlocutor.get_feature('birthmark')
        else:
            return '-'

    @property
    def interlocutor_freckles(self):
        """Return whether the interlocutor has freckles."""
        if self.interlocutor:
            return self.interlocutor.get_feature('freckles')
        else:
            return '-'

    @property
    def interlocutor_glasses(self):
        """Return whether the interlocutor wears glasses."""
        if self.interlocutor:
            return self.interlocutor.get_feature('glasses')
        else:
            return '-'

    @property
    def interlocutor_knowledge_of_subject_first_name(self):
        """Return the interlocutor's conception of the subject of conversation's first name."""
        if self.player.subject_of_conversation in self.interlocutor.mind.mental_models:
            mental_model = self.interlocutor.mind.mental_models[self.player.subject_of_conversation]
            facet = mental_model.name.first_name
            if facet == '':
                facet = '[forgot]'
            return "{value} ({confidence})".format(
                value=facet if facet else '?',
                confidence='-' if not facet or facet == '[forgot]' else facet.strength_str
            )
        else:
            return ''

    @property
    def interlocutor_knowledge_of_subject_last_name(self):
        """Return the interlocutor's conception of the subject of conversation's middle name."""
        if self.player.subject_of_conversation in self.interlocutor.mind.mental_models:
            mental_model = self.interlocutor.mind.mental_models[self.player.subject_of_conversation]
            facet = mental_model.name.last_name
            if facet == '':
                facet = '[forgot]'
            return "{value} ({confidence})".format(
                value=facet if facet else '?',
                confidence='-' if not facet or facet == '[forgot]' else facet.strength_str
            )
        else:
            return ''

    @property
    def interlocutor_knowledge_of_subject_status(self):
        """Return the interlocutor's conception of the subject of conversation's status."""
        if self.player.subject_of_conversation in self.interlocutor.mind.mental_models:
            mental_model = self.interlocutor.mind.mental_models[self.player.subject_of_conversation]
            facet = mental_model.status.status
            if facet == '':
                facet = '[forgot]'
            return "{value} ({confidence})".format(
                value=facet if facet else '?',
                confidence='-' if not facet or facet == '[forgot]' else facet.strength_str
            )
        else:
            return ''

    @property
    def interlocutor_knowledge_of_subject_death_year(self):
        """Return the interlocutor's conception of the subject of conversation's death year."""
        if self.player.subject_of_conversation in self.interlocutor.mind.mental_models:
            mental_model = self.interlocutor.mind.mental_models[self.player.subject_of_conversation]
            facet = mental_model.age.death_year
            if facet == '':
                facet = '[forgot]'
            return "{value} ({confidence})".format(
                value=facet if facet else '?',
                confidence='-' if not facet or facet == '[forgot]' else facet.strength_str
            )
        else:
            return ''

    @property
    def interlocutor_knowledge_of_subject_departure_year(self):
        """Return the interlocutor's conception of the subject of conversation's departure year."""
        if self.player.subject_of_conversation in self.interlocutor.mind.mental_models:
            mental_model = self.interlocutor.mind.mental_models[self.player.subject_of_conversation]
            facet = mental_model.status.departure_year
            if facet == '':
                facet = '[forgot]'
            return "{value} ({confidence})".format(
                value=facet if facet else '?',
                confidence='-' if not facet or facet == '[forgot]' else facet.strength_str
            )
        else:
            return ''

    @property
    def interlocutor_knowledge_of_subject_relations_to_them(self):
        """Return the interlocutor's conception of the subject of conversation's relations to them."""
        if self.player.subject_of_conversation in self.interlocutor.mind.mental_models:
            mental_model = self.interlocutor.mind.mental_models[self.player.subject_of_conversation]
            relations_to_me = list(mental_model.relations_to_me)
            if len(relations_to_me) > 1:
                and_n_more_str = " (and {} more)".format(len(relations_to_me)-1)
            else:
                and_n_more_str = ""
            return "{relation}{and_n_more}".format(
                relation='None' if not relations_to_me else relations_to_me[0][0],
                and_n_more=and_n_more_str
            )
        else:
            return ''

    @property
    def interlocutor_charge_of_subject(self):
        """Return the interlocutor's conception of the subject of conversation's relations to them."""
        if self.player.subject_of_conversation in self.interlocutor.mind.mental_models:
            if self.player.subject_of_conversation in self.interlocutor.relationships:
                charge_str = self.interlocutor.relationships[self.player.subject_of_conversation].charge_str
            else:
                charge_str = '-'
            return charge_str
        else:
            return ''

    @property
    def interlocutor_spark_of_subject(self):
        """Return the interlocutor's charge toward the subject of conversation."""
        if self.player.subject_of_conversation in self.interlocutor.mind.mental_models:
            if self.player.subject_of_conversation in self.interlocutor.relationships:
                spark_str = self.interlocutor.relationships[self.player.subject_of_conversation].spark_str
            else:
                spark_str = '-'
            return spark_str
        else:
            return ''

    @property
    def interlocutor_knowledge_of_subject_age(self):
        """Return the interlocutor's conception of the subject of conversation's age."""
        if self.player.subject_of_conversation in self.interlocutor.mind.mental_models:
            mental_model = self.interlocutor.mind.mental_models[self.player.subject_of_conversation]
            if mental_model.age.exact and mental_model.age.exact != '':
                if mental_model.age.death_year and mental_model.age.death_year != 'None':
                    least_confident_about = min(
                        mental_model.age.birth_year, mental_model.age.death_year, key=lambda facet: facet.strength
                    )
                    strength_str = least_confident_about.strength_str
                else:
                    # Owner believes person is still alive, so strength of this exact-age
                    # belief is actually just the strength of the belief about the birth year
                    strength_str = mental_model.age.birth_year.strength_str
                return "{exact_age} ({confidence})".format(
                    exact_age=mental_model.age.exact,
                    confidence=strength_str
                )
            else:
                facet = mental_model.age.approximate
                if facet == '':
                    facet = '[forgot]'
                return "{value} ({confidence})".format(
                    value=facet if facet else '?',
                    confidence='-' if not facet or facet == '[forgot]' else facet.strength_str
                )
        else:
            return ''

    @property
    def interlocutor_knowledge_of_subject_home_address(self):
        """Return the interlocutor's conception of the subject of conversation's home address."""
        if self.player.subject_of_conversation in self.interlocutor.mind.mental_models:
            mental_model = self.interlocutor.mind.mental_models[self.player.subject_of_conversation]
            facet = mental_model.home.mental_model.address
            if facet == '':
                facet = '[forgot]'
            return "{value} ({confidence})".format(
                value=facet if facet else '?',
                confidence='-' if not facet or facet == '[forgot]' else facet.strength_str
            )
        else:
            return ''

    @property
    def interlocutor_knowledge_of_subject_job_status_and_title(self):
        """Return the interlocutor's conception of the subject of conversation's job status."""
        if self.player.subject_of_conversation in self.interlocutor.mind.mental_models:
            mental_model = self.interlocutor.mind.mental_models[self.player.subject_of_conversation]
            # Job status
            status_facet = mental_model.occupation.status
            if status_facet == '':
                status_facet = '[forgot status]'
            status_component = "{value} ({confidence})".format(
                value=status_facet if status_facet else '?',
                confidence='-' if not status_facet or status_facet == '[forgot]' else status_facet.strength_str
            )
            # Job title
            title_facet = mental_model.occupation.job_title
            if title_facet == '':
                title_facet = '[forgot title]'
            title_component = "{value} ({confidence})".format(
                value=title_facet if title_facet else '?',
                confidence='-' if not title_facet or title_facet == '[forgot]' else title_facet.strength_str
            )
            return '{} {}'.format(status_component, title_component)
        else:
            return ''

    @property
    def interlocutor_knowledge_of_subject_job_shift(self):
        """Return the interlocutor's conception of the subject of conversation's job shift."""
        if self.player.subject_of_conversation in self.interlocutor.mind.mental_models:
            mental_model = self.interlocutor.mind.mental_models[self.player.subject_of_conversation]
            facet = mental_model.occupation.shift
            if facet == '':
                facet = '[forgot]'
            return "{value} ({confidence})".format(
                value=facet if facet else '?',
                confidence='-' if not facet or facet == '[forgot]' else facet.strength_str
            )
        else:
            return ''

    @property
    def interlocutor_knowledge_of_subject_workplace(self):
        """Return the interlocutor's conception of the subject of conversation's workplace."""
        if self.player.subject_of_conversation in self.interlocutor.mind.mental_models:
            mental_model = self.interlocutor.mind.mental_models[self.player.subject_of_conversation]
            facet = mental_model.occupation.company
            if facet and facet.object_itself and facet.object_itself.out_of_business:
                company_out_of_business = True
            else:
                company_out_of_business = False
            if facet == '':
                facet = '[forgot]'
            return "{out_of_business_marker}{value} ({confidence})".format(
                out_of_business_marker='[OOB] ' if company_out_of_business else '',
                value=facet if facet else '?',
                confidence='-' if not facet or facet == '[forgot]' else facet.strength_str
            )
        else:
            return ''

    @property
    def interlocutor_knowledge_of_subject_skin_color(self):
        """Return the interlocutor's conception of the subject of conversation's skin color."""
        if self.player.subject_of_conversation in self.interlocutor.mind.mental_models:
            broader_skin_tone = {
                'black': 'dark', 'brown': 'dark',
                'beige': 'light', 'pink': 'light',
                'white': 'light', '[forgot]': '[forgot]'
            }
            mental_model = self.interlocutor.mind.mental_models[self.player.subject_of_conversation]
            facet = mental_model.face.skin.color
            if facet == '':
                facet = '[forgot]'
            return "{tone} ({confidence})".format(
                tone=broader_skin_tone[facet] if mental_model.face.skin.color else '?',
                confidence='-' if not mental_model.face.skin.color or facet == '[forgot]' else
                mental_model.face.skin.color.strength_str
            )
        else:
            return ''

    @property
    def interlocutor_knowledge_of_subject_hair_color(self):
        """Return the interlocutor's conception of the subject of conversation's hair color."""
        if self.player.subject_of_conversation in self.interlocutor.mind.mental_models:
            mental_model = self.interlocutor.mind.mental_models[self.player.subject_of_conversation]
            facet = mental_model.face.hair.color
            if facet == '':
                facet = '[forgot]'
            return "{value} ({confidence})".format(
                value=facet if facet else '?',
                confidence='-' if not facet or facet == '[forgot]' else facet.strength_str
            )
        else:
            return ''

    @property
    def interlocutor_knowledge_of_subject_hair_length(self):
        """Return the interlocutor's conception of the subject of conversation's hair length."""
        if self.player.subject_of_conversation in self.interlocutor.mind.mental_models:
            mental_model = self.interlocutor.mind.mental_models[self.player.subject_of_conversation]
            facet = mental_model.face.hair.length
            if facet == '':
                facet = '[forgot]'
            return "{value} ({confidence})".format(
                value=facet if facet else '?',
                confidence='-' if not facet or facet == '[forgot]' else facet.strength_str
            )
        else:
            return ''

    @property
    def interlocutor_knowledge_of_subject_facial_hair(self):
        """Return the interlocutor's conception of the subject of conversation's facial hair style, if any."""
        if self.player.subject_of_conversation in self.interlocutor.mind.mental_models:
            mental_model = self.interlocutor.mind.mental_models[self.player.subject_of_conversation]
            facet = mental_model.face.facial_hair.style
            if facet == '':
                facet = '[forgot]'
            return "{value} ({confidence})".format(
                value=facet if facet else '?',
                confidence='-' if not facet or facet == '[forgot]' else facet.strength_str
            )
        else:
            return ''

    @property
    def interlocutor_knowledge_of_subject_tattoo(self):
        """Return the interlocutor's conception of the subject of conversation's tattoo, if any."""
        if self.player.subject_of_conversation in self.interlocutor.mind.mental_models:
            mental_model = self.interlocutor.mind.mental_models[self.player.subject_of_conversation]
            facet = mental_model.face.distinctive_features.tattoo
            if facet == '':
                facet = '[forgot]'
            return "{value} ({confidence})".format(
                value=facet if facet else '?',
                confidence='-' if not facet or facet == '[forgot]' else facet.strength_str
            )
        else:
            return ''

    @property
    def interlocutor_knowledge_of_subject_scar(self):
        """Return the interlocutor's conception of the subject of conversation's scar, if any."""
        if self.player.subject_of_conversation in self.interlocutor.mind.mental_models:
            mental_model = self.interlocutor.mind.mental_models[self.player.subject_of_conversation]
            facet = mental_model.face.distinctive_features.scar
            if facet == '':
                facet = '[forgot]'
            return "{value} ({confidence})".format(
                value=facet if facet else '?',
                confidence='-' if not facet or facet == '[forgot]' else facet.strength_str
            )
        else:
            return ''

    @property
    def interlocutor_knowledge_of_subject_birthmark(self):
        """Return the interlocutor's conception of the subject of conversation's birthmark, if any."""
        if self.player.subject_of_conversation in self.interlocutor.mind.mental_models:
            mental_model = self.interlocutor.mind.mental_models[self.player.subject_of_conversation]
            facet = mental_model.face.distinctive_features.birthmark
            if facet == '':
                facet = '[forgot]'
            return "{value} ({confidence})".format(
                value=facet if facet else '?',
                confidence='-' if not facet or facet == '[forgot]' else facet.strength_str
            )
        else:
            return ''

    @property
    def interlocutor_knowledge_of_subject_freckles(self):
        """Return the interlocutor's conception of the subject of conversation's freckles, if any."""
        if self.player.subject_of_conversation in self.interlocutor.mind.mental_models:
            mental_model = self.interlocutor.mind.mental_models[self.player.subject_of_conversation]
            facet = mental_model.face.distinctive_features.freckles
            if facet == '':
                facet = '[forgot]'
            return "{value} ({confidence})".format(
                value=facet if facet else '?',
                confidence='-' if not facet or facet == '[forgot]' else facet.strength_str
            )
        else:
            return ''

    @property
    def interlocutor_knowledge_of_subject_glasses(self):
        """Return the interlocutor's conception of the subject of conversation's glasses, if any."""
        if self.player.subject_of_conversation in self.interlocutor.mind.mental_models:
            mental_model = self.interlocutor.mind.mental_models[self.player.subject_of_conversation]
            facet = mental_model.face.distinctive_features.glasses
            if facet == '':
                facet = '[forgot]'
            return "{value} ({confidence})".format(
                value=facet if facet else '?',
                confidence='-' if not facet or facet == '[forgot]' else facet.strength_str
            )
        else:
            return ''

    @property
    def interlocutor_knowledge_of_subject_spouse(self):
        """Return the interlocutor's conception of the subject of conversation's spouse, if any."""
        if self.player.subject_of_conversation in self.interlocutor.mind.mental_models:
            if (self.player.subject_of_conversation.spouse and
                    self.player.subject_of_conversation.spouse in self.interlocutor.mind.mental_models):
                mental_model = self.interlocutor.mind.mental_models[self.player.subject_of_conversation.spouse]
                facet = "{nok_marker}{first_name} {last_name} ({status})".format(
                    nok_marker='!' if self.player.subject_of_conversation.spouse in self.game.next_of_kin else '',
                    first_name=mental_model.name.first_name if mental_model.name.first_name else '?',
                    last_name=mental_model.name.last_name if mental_model.name.last_name else '?',
                    status=mental_model.status.status if mental_model.status.status else '?'
                )
                return facet
            else:
                # Either no spouse, or no spouse in interlocutor's mental models, so return
                # the marital status then
                subject = self.player.subject_of_conversation
                facet_object = self.interlocutor.mind.mental_models[subject].status.marital_status
                if facet_object:
                    confidence = facet_object.strength_str
                    facet = '{marital_status} ({confidence})'.format(
                        marital_status=facet_object,
                        confidence=confidence
                    )
                else:
                    facet = '? (-)'
                return facet
        else:
            return ''

    @property
    def interlocutor_knowledge_of_subject_parents(self):
        """Return the interlocutor's conception of the subject of conversation's parents, if any."""
        if self.player.subject_of_conversation in self.interlocutor.mind.mental_models:
            parents = [
                p for p in self.player.subject_of_conversation.parents if
                p in self.interlocutor.mind.mental_models
            ]
            parents.sort(key=lambda p: p.present, reverse=True)
            if parents:
                names_str = ', '.join(
                    '{}{} {} ({})'.format(
                        '!' if p in self.game.next_of_kin else '',
                        self.interlocutor.mind.mental_models[p].name.first_name if
                        self.interlocutor.mind.mental_models[p].name.first_name else '?',
                        self.interlocutor.mind.mental_models[p].name.last_name if
                        self.interlocutor.mind.mental_models[p].name.last_name else '?',
                        self.interlocutor.mind.mental_models[p].status.status if
                        self.interlocutor.mind.mental_models[p].status.status else '?'
                    )
                    for p in parents
                )
                return names_str
            else:
                return '?'
        return ''

    @property
    def interlocutor_knowledge_of_subject_kids(self):
        """Return the interlocutor's conception of the subject of conversation's kids, if any."""
        if self.player.subject_of_conversation in self.interlocutor.mind.mental_models:
            kids = [
                k for k in self.player.subject_of_conversation.kids if
                k in self.interlocutor.mind.mental_models
            ]
            kids.sort(key=lambda p: p.present, reverse=True)
            if kids:
                names_str = ', '.join(
                    '{}{} {} ({})'.format(
                        '!' if k in self.game.next_of_kin else '',
                        self.interlocutor.mind.mental_models[k].name.first_name if
                        self.interlocutor.mind.mental_models[k].name.first_name else '?',
                        self.interlocutor.mind.mental_models[k].name.last_name if
                        self.interlocutor.mind.mental_models[k].name.last_name else '?',
                        self.interlocutor.mind.mental_models[k].status.status if
                        self.interlocutor.mind.mental_models[k].status.status else '?'
                    )
                    for k in kids
                )
                return names_str
            else:
                return '?'
        return ''

    @property
    def interlocutor_knowledge_of_subject_siblings(self):
        """Return the interlocutor's conception of the subject of conversation's siblings, if any."""
        if self.player.subject_of_conversation in self.interlocutor.mind.mental_models:
            siblings = [
                s for s in self.player.subject_of_conversation.siblings if
                s in self.interlocutor.mind.mental_models
            ]
            siblings.sort(key=lambda p: p.present, reverse=True)
            if siblings:
                names_str = ', '.join(
                    '{}{} {} ({})'.format(
                        '!' if s in self.game.next_of_kin else '',
                        self.interlocutor.mind.mental_models[s].name.first_name if
                        self.interlocutor.mind.mental_models[s].name.first_name else '?',
                        self.interlocutor.mind.mental_models[s].name.last_name if
                        self.interlocutor.mind.mental_models[s].name.last_name else '?',
                        self.interlocutor.mind.mental_models[s].status.status if
                        self.interlocutor.mind.mental_models[s].status.status else '?'
                    )
                    for s in siblings
                )
                return names_str
            else:
                return '?'
        return ''

    @property
    def interlocutor_knowledge_of_subject_extended_family(self):
        """Return the interlocutor's conception of the subject of conversation's extended family, if any."""
        if self.player.subject_of_conversation in self.interlocutor.mind.mental_models:
            subject = self.player.subject_of_conversation
            subject_extended_family = (
                # Build this set manually to preclude in-laws being included
                subject.greatgrandparents | subject.grandparents | subject.aunts | subject.uncles |
                subject.nieces | subject.nephews | subject.cousins
            )
            known_extended_family = [
                ef for ef in subject_extended_family if
                ef in self.interlocutor.mind.mental_models and
                ef not in self.player.subject_of_conversation.immediate_family
            ]
            # Sort so people still in town show up first
            known_extended_family.sort(key=lambda p: p.present, reverse=True)
            if known_extended_family:
                names_str = ', '.join(
                    '{}{} {} ({}; {})'.format(
                        '!' if ef in self.game.next_of_kin else '',
                        self.interlocutor.mind.mental_models[ef].name.first_name if
                        self.interlocutor.mind.mental_models[ef].name.first_name else '?',
                        self.interlocutor.mind.mental_models[ef].name.last_name if
                        self.interlocutor.mind.mental_models[ef].name.last_name else '?',
                        self.player.subject_of_conversation.relation_to_me(ef),
                        self.interlocutor.mind.mental_models[ef].status.status if
                        self.interlocutor.mind.mental_models[ef].status.status else '?'
                    )
                    for ef in known_extended_family
                )
                return names_str
            else:
                return '?'
        return ''

    @property
    def last_interlocutor(self):
        """Return the last interlocutor actor played (prior to the current one)."""
        if not self.player.interlocutor:
            if self.player.all_interlocutors:
                return self.player.all_interlocutors[-1]
            else:
                return ''
        else:
            if len(self.player.all_interlocutors) > 1:
                return self.player.all_interlocutors[-2]
            else:
                return ''

    @property
    def last_interlocutor_name(self):
        """Return the name of the last interlocutor actor played."""
        if self.last_interlocutor:
            if self.last_interlocutor in self.game.next_of_kin:
                return '!' + self.last_interlocutor.name
            else:
                return self.last_interlocutor.name
        else:
            return ''

    @property
    def last_interlocutor_description(self):
        """Return a short description of the last interlocutor actor played."""
        last_interlocutor = self.last_interlocutor
        if not last_interlocutor:
            return ''
        if last_interlocutor.occupation:
            occupation = last_interlocutor.occupation.vocation
        elif last_interlocutor.retired:
            occupation = 'retiree'
        elif last_interlocutor.age < 18:
            occupation = 'student'
        elif last_interlocutor.female and last_interlocutor.kids_at_home:
            occupation = 'stay-at-home mom'
        else:
            occupation = 'person'
        return "{age}-year-old {occupation}".format(
            age=last_interlocutor.age, occupation=occupation
        )

    @property
    def penultimate_interlocutor(self):
        """Return the penultimate interlocutor that actor played."""
        if not self.player.interlocutor:
            if len(self.player.all_interlocutors) > 1:
                return self.player.all_interlocutors[-2]
            else:
                return ''
        else:
            if len(self.player.all_interlocutors) > 2:
                return self.player.all_interlocutors[-3]
            else:
                return ''

    @property
    def penultimate_interlocutor_name(self):
        """Return the name of the penultimate interlocutor actor played."""
        if self.penultimate_interlocutor:
            if self.penultimate_interlocutor in self.game.next_of_kin:
                return '!' + self.penultimate_interlocutor.name
            else:
                return self.penultimate_interlocutor.name
        else:
            return ''

    @property
    def penultimate_interlocutor_description(self):
        """Return a short description of the penultimate interlocutor actor played."""
        penultimate_interlocutor = self.penultimate_interlocutor
        if not penultimate_interlocutor:
            return ''
        if penultimate_interlocutor.occupation:
            occupation = penultimate_interlocutor.occupation.vocation
        elif penultimate_interlocutor.retired:
            occupation = 'retiree'
        elif penultimate_interlocutor.age < 18:
            occupation = 'student'
        elif penultimate_interlocutor.female and penultimate_interlocutor.kids_at_home:
            occupation = 'stay-at-home mom'
        else:
            occupation = 'person'
        return "{age}-year-old {occupation}".format(
            age=penultimate_interlocutor.age, occupation=occupation
        )

    @property
    def antepenultimate_interlocutor(self):
        """Return the antepenultimate interlocutor that actor played."""
        if not self.player.interlocutor:
            if len(self.player.all_interlocutors) > 2:
                return self.player.all_interlocutors[-3]
            else:
                return ''
        else:
            if len(self.player.all_interlocutors) > 3:
                return self.player.all_interlocutors[-4]
            else:
                return ''

    @property
    def antepenultimate_interlocutor_name(self):
        """Return the name of the antepenultimate interlocutor actor played."""
        if self.antepenultimate_interlocutor:
            if self.antepenultimate_interlocutor in self.game.next_of_kin:
                return '!' + self.antepenultimate_interlocutor.name
            else:
                return self.antepenultimate_interlocutor.name
        else:
            return ''

    @property
    def antepenultimate_interlocutor_description(self):
        """Return a short description of the antepenultimate interlocutor actor played."""
        antepenultimate_interlocutor = self.antepenultimate_interlocutor
        if not antepenultimate_interlocutor:
            return ''
        if antepenultimate_interlocutor.occupation:
            occupation = antepenultimate_interlocutor.occupation.vocation
        elif antepenultimate_interlocutor.retired:
            occupation = 'retiree'
        elif antepenultimate_interlocutor.age < 18:
            occupation = 'student'
        elif antepenultimate_interlocutor.female and antepenultimate_interlocutor.kids_at_home:
            occupation = 'stay-at-home mom'
        else:
            occupation = 'person'
        return "{age}-year-old {occupation}".format(
            age=antepenultimate_interlocutor.age, occupation=occupation
        )

    @property
    def next_of_kin_description(self):
        """An expression of all the next of kin to afford actor drama management."""
        description = ''
        for i in xrange(len(self.game.next_of_kin)):
            nok = self.game.next_of_kin[i]
            name = '!' + nok.name
            relation_to_interlocutor = 'n/a' if not self.interlocutor else self.interlocutor.relation_to_me(nok)
            current_location = nok.location.name
            description += '{comma}{name} (my {relation_to_i}; at {current_location})'.format(
                comma=', ' if i != 0 else '',
                name=name,
                relation_to_i=relation_to_interlocutor,
                current_location=current_location
            )
        return description

    @property
    def interlocutor_sources_of_knowledge_about_subject(self):
        """An expression of the interlocutor's sources for the knowledge they have about subject."""
        str_representation = ''
        for i in xrange(len(self.interlocutor_source_distribution)):
            source, percentage = self.interlocutor_source_distribution[i]
            str_representation += '{comma}{source} ({percentage}%)'.format(
                comma=', ' if i != 0 else '',
                source='myself' if source is self.interlocutor else source.name,
                percentage=int(round(percentage*100))
            )
        return str_representation