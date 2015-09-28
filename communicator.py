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
        # Text that is displayed to the player at any given point during gameplay; updated
        # periodically by the gameplay instance
        self.player_exposition = ''
        self.player_exposition_enumeration = ''  # Enumeration of buildings, characters nearby, etc.
        # Load templates
        template_loader = jinja2.FileSystemLoader(searchpath="./templates")
        template_env = jinja2.Environment(loader=template_loader)
        self.player_template = template_env.get_template('player.html')
        self.actor_template = template_env.get_template('actor.html')

    def update_player_interface(self):
        """Update the player interface by re-writing its HTML file.

        NOTE: It is the responsibility of the web browser that we have set up for
        the player to constantly be reloading this page.
        """
        # Fill in the template
        rendered_player_template = self.player_template.render(communicator=self)
        # Write that out as a local file
        f = open(PATH_TO_PLAYER_INTERFACE_HTML_FILE, 'w')
        f.write(rendered_player_template)
        f.close()
        # SCP that local file so that it is web-facing from my BSOE account
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.connect(hostname='soe.ucsc.edu', username='jor', password=ZZZ)
        scp = SCPClient(ssh.get_transport())
        scp.put(PATH_TO_PLAYER_INTERFACE_HTML_FILE, '~/.html/bad_news/player.html')

    def update_actor_interface(self):
        """Update the actor interface by re-writing its HTML file.

        NOTE: It is the responsibility of the web browser that we have set up for
        the actor to constantly be reloading this page.
        """
        # Fill in the template
        rendered_actor_template = self.actor_template.render(communicator=self)
        # Write that out as a local file
        f = open(PATH_TO_ACTOR_INTERFACE_HTML_FILE, 'w')
        f.write(rendered_actor_template)
        f.close()
        # SCP that local file so that it is web-facing from my BSOE account
        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.connect(hostname='soe.ucsc.edu', username='jor', password=ZZZ)
        scp = SCPClient(ssh.get_transport())
        scp.put(PATH_TO_ACTOR_INTERFACE_HTML_FILE, '~/.html/bad_news/actor.html')

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
                        ', '.join(p.name for p in self.interlocutor.location.people_here_now-{self.interlocutor})
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
            workplace = self.interlocutor.get_feature('workplace')
            if self.interlocutor.occupation:
                workplace += ' (since {})'.format(self.interlocutor.occupation.start_date)
            return workplace
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