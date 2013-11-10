import random
import sys

from swallows.engine.events import Event

### TOPICS ###

# a "topic" is just what a character has recently had addressed to
# them.  It could be anything, not just words, by another character
# (for example, a gesture.)

class Topic(object):
    def __init__(self, originator, subject=None):
        self.originator = originator
        self.subject = subject


class GreetTopic(Topic):
    pass


class SpeechTopic(Topic):
    pass


class QuestionTopic(Topic):
    pass


### BELIEFS ###

#
# a belief is something an Animate believes.  they come in a few types:
#
# - a belief that an object is somewhere
#   - because they saw it there (memory)
#   - because some other character told them it was there
# - a belief that they should do something (a goal), which has subtypes:
#   - a belief that an object is desirable & they should try to acquire it
#   - a belief that something should be done about something (bland, general)
# - a belief that another Animate believes something
#
# of course, any particular belief may turn out not to be true
#

# abstract base class
class Belief(object):
    # constructor of all subclasses of this class should accept being
    # called with only one argument, as a convenience sort of thing
    # for BeliefSet.get and .remove, which don't really care about anything
    # about the Belief except for its class and its subject.
    # although, usually, you do want to pass more than one argument when
    # making a real Belief to pass to BeliefSet.add.  (clear as mud, right?)
    def __init__(self, subject):          # kind of silly for an ABC to have a
        assert isinstance(subject, Actor) # constructor, but it is to emphasize
        self.subject = subject            # that all beliefs have a subject,
                                          # which is the thing we believe
                                          # something about

    def __str__(self):
        raise NotImplementedError


class ItemLocation(Belief):   # formerly "Memory"
    def __init__(self, subject, location=None, informant=None, concealer=None):
        assert isinstance(subject, Actor)
        assert isinstance(location, Actor) or location is None
        self.subject = subject      # the thing we think is somewhere
        self.location = location    # the place we think it is
        self.informant = informant  # the actor who told us about it
        self.concealer = concealer  # the actor who we think hid it ther

    def __str__(self):
        s = "%s is in %s" % (
            self.subject.render([]),
            self.location.render([])
        )
        if self.concealer:
            s += " (hidden there by %s)" % self.concealer.render([])
        if self.informant:
            s += " (%s told me so)" % self.informant.render([])
        return s


class Goal(Belief):
    def __init__(self, subject, phrase=None):
        assert isinstance(subject, Actor)
        self.subject = subject   # the thing we would like to do something about
        self.phrase = phrase     # human-readable description

    def __str__(self):
        return "I should %s %s" % (
            self.phrase,
            self.subject.render([])
        )


class Desire(Goal):
    def __init__(self, subject):
        assert isinstance(subject, Actor)
        self.subject = subject   # the thing we would like to acquire

    def __str__(self):
        return "I want %s" % (
            self.subject.render([])
        )


# oh dear
class BeliefsBelief(Belief):
    def __init__(self, subject, belief_set=None):
        assert isinstance(subject, Animate)
        self.subject = subject        # the animate we think holds the belief
        if belief_set is None:
            belief_set = BeliefSet()
        assert isinstance(belief_set, BeliefSet)
        self.belief_set = belief_set  # the beliefs we think they hold

    def __str__(self):
        return "%s believes { %s }" % (
            self.subject.render([]),
            self.belief_set
        )


class BeliefSet(object):
    """A BeliefSet works something like a Python set(), but has the
    following constraints:
    
    There can be only one of each type of Belief about a particular
    item in the set.

    So it's really kind of a map from Actors to maps from Belief
    subclasses to Beliefs.

    But it behooves us (or at least, me) to think of it as a set.
    (Besides, it might change.)

    """
    def __init__(self):
        self.belief_map = {}

    def add(self, belief):
        assert isinstance(belief, Belief)
        subject = belief.subject
        self.belief_map.setdefault(subject, {})[belief.__class__] = belief

    def remove(self, belief):
        # the particular belief passed to us doesn't really matter.  we extract
        # the class and subject and return any existing belief we may have
        assert isinstance(belief, Belief)
        subject = belief.subject
        self.belief_map.setdefault(subject, {})[belief.__class__] = None

    def get(self, belief):
        # the particular belief passed to us doesn't really matter.  we extract
        # the class and subject and return any existing belief we may have
        assert isinstance(belief, Belief)
        subject = belief.subject
        return self.belief_map.setdefault(subject, {}).get(
            belief.__class__, None
        )

    def subjects(self):
        for subject in self.belief_map:
            yield subject

    def beliefs_for(self, subject):
        # assert belief_class descends from Belief
        beliefs = self.belief_map.setdefault(subject, {})
        for class_ in beliefs:
            yield beliefs[class_]

    def __str__(self):
        l = []
        for subject in self.subjects():
            for belief in self.beliefs_for(subject):
                l.append(str(belief))
        return ', '.join(l)


### ACTORS (objects in the world) ###

class Actor(object):
    def __init__(self, name, location=None, collector=None):
        self.name = name
        self.collector = collector
        self.contents = set()
        self.enter = ""
        self.location = None
        if location is not None:
            self.move_to(location)

    def notable(self):
        return self.treasure() or self.weapon() or self.animate() or self.horror()

    def treasure(self):
        return False

    def weapon(self):
        return False

    def horror(self):
        return False

    def takeable(self):
        return False

    def animate(self):
        return False

    def container(self):
        return False

    def article(self):
        return 'the'

    def posessive(self):
        return "its"

    def accusative(self):
        return "it"

    def pronoun(self):
        return "it"

    def was(self):
        return "was"

    def is_(self):
        return "is"

    def emit(self, *args, **kwargs):
        if self.collector:
            self.collector.collect(Event(*args, **kwargs))

    def move_to(self, location):
        if self.location:
            self.location.contents.remove(self)
        self.location = location
        self.location.contents.add(self)

    def render(self, participants):
        name = self.name
        if participants:
            subject = participants[0]
            posessive = subject.name + "'s"
            name = name.replace(posessive, subject.posessive())
        article = self.article()
        if not article:
            return name
        return '%s %s' % (article, name)

    def indefinite(self):
        article = 'a'
        if self.name.startswith(('a', 'e', 'i', 'o', 'u')):
            article = 'an'
        return '%s %s' % (article, self.name)


### some mixins for Actors ###

class ProperMixin(object):
    def article(self):
        return ''


class PluralMixin(object):
    def posessive(self):
        return "their"

    def accusative(self):
        return "them"

    def pronoun(self):
        return "they"

    def indefinite(self):
        article = 'some'
        return '%s %s' % (article, self.name)

    def was(self):
        return "were"

    def is_(self):
        return "are"


class MasculineMixin(object):
    def posessive(self):
        return "his"

    def accusative(self):
        return "him"

    def pronoun(self):
        return "he"


class FeminineMixin(object):
    def posessive(self):
        return "her"

    def accusative(self):
        return "her"

    def pronoun(self):
        return "she"


### ANIMATE OBJECTS ###

class Animate(Actor):
    def __init__(self, name, location=None, collector=None):
        Actor.__init__(self, name, location=location, collector=None)
        self.topic = None
        self.beliefs = BeliefSet()

    def animate(self):
        return True

    # for debugging
    def dump_beliefs(self):
        for subject in self.beliefs.subjects():
            for belief in self.beliefs.beliefs_for(subject):
                print ".oO{ %s }" % belief

    ###--- belief accessors/manipulators ---###
    
    # these are mostly just aliases for accessing the BeliefSet.

    def remember_location(self, thing, location, concealer=None):
        """Update this Animate's beliefs to include a belief that the
        given thing is located at the given location.

        Really just a readable alias for believe_location.

        """
        self.believe_location(thing, location, informant=None, concealer=concealer)

    def believe_location(self, thing, location, informant=None, concealer=None):
        """Update this Animate's beliefs to include a belief that the
        given thing is located at the given location.  They may have
        been told this by someone.

        """
        self.beliefs.add(ItemLocation(
            thing, location, informant=informant, concealer=concealer
        ))

    def recall_location(self, thing):
        """Return an ItemLocation (belief) about this thing, or None."""
        return self.beliefs.get(ItemLocation(thing))

    def forget_location(self, thing):
        self.beliefs.remove(ItemLocation(thing))

    def desire(self, thing):
        self.beliefs.add(Desire(thing))

    def quench_desire(self, thing):
        # usually called when it has been acquired
        self.beliefs.remove(Desire(thing))

    def does_desire(self, thing):
        if thing.treasure():
            return True  # omg YES
        if thing.weapon():
            return True  # could come in handy.  (TODO, sophisticate this?)
        return self.beliefs.get(Desire(thing)) is not None

    def believed_beliefs_of(self, other):
        """Returns a BeliefSet (not a Belief) that this Animate
        believes the other Animate holds.

        Typically you would manipulate this BeliefSet directly
        with add, remove, get, etc.

        """
        assert isinstance(other, Animate)
        # for extra fun, try reading the code of this method out loud!
        beliefs_belief = self.beliefs.get(BeliefsBelief(other))
        if beliefs_belief is None:
            beliefs_belief = BeliefsBelief(other, BeliefSet())
            self.beliefs.add(beliefs_belief)
        return beliefs_belief.belief_set

    ###--- topic stuff ---###

    def address(self, other, topic, phrase, participants=None):
        if participants is None:
            participants = [self, other]
        other.topic = topic
        self.emit(phrase, participants)

    def greet(self, other, phrase, participants=None):
        self.address(other, GreetTopic(self), phrase, participants)

    def speak_to(self, other, phrase, participants=None, subject=None):
        self.address(other, SpeechTopic(self, subject=subject), phrase, participants)

    def question(self, other, phrase, participants=None, subject=None):
        self.address(other, QuestionTopic(self, subject=subject), phrase, participants)

    ###--- generic actions ---###

    def place_in(self, location):
        # like move_to but quieter; for setting up scenes etc
        if self.location is not None:
            self.location.contents.remove(self)
        self.location = location
        self.location.contents.add(self)
        # this is needed so that the Editor knows where the character starts
        # (it is possible a future Editor might be able to strip out
        # instances of these that aren't informative, though)
        self.emit("<1> <was-1> in <2>", [self, self.location])
        # a side-effect of the following code is, if they start in a location
        # with a horror,they don't react to it.  They probably should.
        for x in self.location.contents:
            if x == self:
                continue
            if x.notable():
                self.emit("<1> saw <2>", [self, x])
                self.remember_location(x, self.location)

    def move_to(self, location):
        assert(location != self.location)
        assert(location is not None)
        for x in self.location.contents:
            # otherwise we get "Bob saw Bob leave the room", eh?
            if x is self:
                continue
            if x.animate():
                x.emit("<1> saw <2> leave the %s" % x.location.noun(), [x, self])
        if self.location is not None:
            self.location.contents.remove(self)
        self.location = location
        assert self not in self.location.contents
        self.location.contents.add(self)
        self.emit("<1> went to <2>", [self, self.location])

    def point_at(self, other, item):
        # it would be nice if there was some way to
        # indicate the revolver as part of the Topic which will follow,
        # or otherwise indicate the context as "at gunpoint"

        assert self.location == other.location
        assert item.location == self
        self.emit("<1> pointed <3> at <2>",
            [self, other, item])
        for actor in self.location.contents:
            if actor.animate():
                actor.remember_location(item, self)

    def put_down(self, item):
        assert(item.location == self)
        self.emit("<1> put down <2>", [self, item])
        item.move_to(self.location)
        for actor in self.location.contents:
            if actor.animate():
                actor.remember_location(item, self.location)

    def pick_up(self, item):
        assert(item.location == self.location)
        self.emit("<1> picked up <2>", [self, item])
        item.move_to(self)
        for actor in self.location.contents:
            if actor.animate():
                actor.remember_location(item, self)

    def give_to(self, other, item):
        assert(item.location == self)
        assert(self.location == other.location)
        self.emit("<1> gave <3> to <2>", [self, other, item])
        item.move_to(other)
        for actor in self.location.contents:
            if actor.animate():
                actor.remember_location(item, other)

    def wander(self):
        self.move_to(
            self.location.exits[
                random.randint(0, len(self.location.exits)-1)
            ]
        )

    def live(self):
        """This gets called on each turn an animate moves.
        
        You need to implement this for particular animates.
        
        """
        raise NotImplementedError(
            'Please implement %s.live()' % self.__class__.__name__
        )


class Male(MasculineMixin, ProperMixin, Animate):
    pass


class Female(FeminineMixin, ProperMixin, Animate):
    pass


### LOCATIONS ###

class Location(Actor):
    def __init__(self, name, enter="went to", noun="room"):
        self.name = name
        self.enter = enter
        self.contents = set()
        self.exits = []
        self.noun_ = noun

    def noun(self):
        return self.noun_

    def set_exits(self, *exits):
        for exit in exits:
            assert isinstance(exit, Location)
        self.exits = exits


class ProperLocation(ProperMixin, Location):
    pass


### OTHER INANIMATE OBJECTS ###

class Item(Actor):
    def takeable(self):
        return True


class Weapon(Item):
    def weapon(self):
        return True


class Container(Actor):
    def container(self):
        return True


class ProperContainer(ProperMixin, Container):
    pass


class Treasure(Item):
    def treasure(self):
        return True


class PluralTreasure(PluralMixin, Treasure):
    pass


class Horror(Actor):
    def horror(self):
        return True
