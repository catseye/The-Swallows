#!/usr/bin/env python

import random
import sys

from swallows.engine.events import Event
from swallows.util import pick

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


### MEMORIES ###

class Memory(object):
    def __init__(self, subject, location, i_hid_it_there=False):
        self.subject = subject  # the thing being remembered
        self.location = location  # where we last remember seeing it
        self.i_hid_it_there = i_hid_it_there


### ACTORS (objects in the world) ###

class Actor(object):
    def __init__(self, name, location=None, collector=None):
        self.name = name
        self.collector = collector
        self.contents = []
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
        self.location.contents.append(self)

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

    # for debugging
    def dump_memory(self):
        for thing in self.memories:
            memory = self.memories[thing]
            print ".oO{ %s is in %s }" % (
                memory.subject.render([]),
                memory.location.render([]))
            if memory.i_hid_it_there:
                print ".oO{ I hid it there }"
        print "desired items:", repr(self.desired_items)
        print "decisions:", repr(self.what_to_do_about)
        print "knowledge of others' decisions:", repr(self.other_decision_about)


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
        # hash of actor object to Memory object
        self.memories = {}
        self.desired_items = set()
        # this should really be *derived* from having a recent memory
        # of seeing a dead body in the bathroom.  but for now,
        self.nerves = 'calm'
        # this, too, should be more sophisticated.
        # it is neither a memory, nor a belief, but a judgment, and
        # eventually possibly a goal.
        # hash maps Actors to strings
        self.what_to_do_about = {}
        self.other_decision_about = {}

    def animate(self):
        return True

    def remember(self, thing, location, i_hid_it_there=False):
        assert isinstance(thing, Actor)
        self.memories[thing] = Memory(thing, location, i_hid_it_there=i_hid_it_there)
    
    def recall(self, thing):
        assert isinstance(thing, Actor)
        return self.memories.get(thing, None)

    def address(self, other, topic, phrase, participants=None):
        if participants is None:
            participants = [self, other]
        other.topic = topic
        # in the absence of a better event-collection system
        # we do this sort of thing when >1 actor can observe an event:
        self.emit(phrase, participants)
        other.emit(phrase, participants)

    def greet(self, other, phrase, participants=None):
        self.address(other, GreetTopic(self), phrase, participants)

    def speak_to(self, other, phrase, participants=None, subject=None):
        self.address(other, SpeechTopic(self, subject=subject), phrase, participants)

    def question(self, other, phrase, participants=None, subject=None):
        self.address(other, QuestionTopic(self, subject=subject), phrase, participants)

    def place_in(self, location):
        # like move_to but quieter; for setting up scenes etc
        if self.location is not None:
            self.location.contents.remove(self)
        self.location = location
        self.location.contents.append(self)
        self.emit("<1> <was-1> in <2>", [self, self.location])
        for x in self.location.contents:
            if x == self:
                continue
            if x.notable():
                self.emit("<1> saw <2>", [self, x])
                self.remember(x, self.location)

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
        self.location.contents.append(self)
        self.emit("<1> went to <2>", [self, self.location])

    def point_at(self, other, item):
        # it would be nice if there was some way to
        # indicate the revolver as part of the Topic which will follow,
        # or otherwise indicate the context as "at gunpoint"

        # XXX SERIOUSLY WE HAVE TO FIX THIS
        # assert self.location == other.location
        assert item.location == self
        self.emit("<1> pointed <3> at <2>",
            [self, other, item])
        other.emit("<1> pointed <3> at <2>",
            [self, other, item])
        other.remember(item, self)

    def put_down(self, item):
        assert(item.location == self)
        self.emit("<1> put down <2>", [self, item])
        item.move_to(self.location)
        self.remember(item, self.location)
        for other in self.location.contents:
            if other is self:
                continue
            if other.animate():
                other.emit("<1> put down <2>", [self, item])
                other.remember(item, self.location)

    def pick_up(self, item):
        assert(item.location == self.location)
        self.emit("<1> picked up <2>", [self, item])
        item.move_to(self)
        self.remember(item, self)
        for other in self.location.contents:
            if other is self:
                continue
            if other.animate():
                other.emit("<1> picked up <2>", [self, item])
                other.remember(item, self)

    def give_to(self, other, item):
        assert(item.location == self)
        # XXX seriously? this isn't preserved? blast
        # assert(self.location == other.location)
        self.emit("<1> gave <3> to <2>", [self, other, item])
        other.emit("<1> gave <3> to <2>", [self, other, item])
        item.move_to(other)
        self.remember(item, other)
        other.remember(item, other)

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
        self.contents = []
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
