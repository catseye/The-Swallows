#!/usr/bin/env python

#
# the_swallows.py: a novel generator.
# Chris Pressey, Cat's Eye Technologies
#

import random
import sys

# TODO
# "in which bob hides the stolen jewels in the mailbox"
# more reacting to the dead body:
# - needing a drink (add liquor cabinet)
# - calling the police
# - trying to dispose of it
# an unspeakable thing in the basement!
# paragraphs should not always be the same number of events.  variety!
# path-finder between any two rooms -- not too difficult, even if it
#   would be nicer in Prolog.
# DRAMATIC IRONY would be really nice, but hard to pull off.
# "it was so nice" -- actually *have* memories of locations, and feelings
#   (good/bad, 0 to 10 or something) about memories
# anxiety memory = the one they're most recently panicked about
# bullets for the revolver
# memory of whether the revolver was loaded last time they saw it
# calling their bluff
# dear me, someone might actually get shot
# "Bob went to Bob's bedroom"
# a better solution for "Bob was in the kitchen" at the start of a paragraph

def pick(l):
    return l[random.randint(0, len(l)-1)]

# this will get filled in later
ALL_ITEMS = []

### EVENTS ###

class Event(object):
    def __init__(self, phrase, participants, excl=False):
        self.phrase = phrase
        self.participants = participants
        self.excl = excl
    
    def __str__(self):
        phrase = self.phrase
        i = 0
        for participant in self.participants:
            phrase = phrase.replace('<%d>' % (i + 1), str(participant))
            phrase = phrase.replace('<indef-%d>' % (i + 1), participant.indefinite())
            phrase = phrase.replace('<his-%d>' % (i + 1), participant.posessive())
            phrase = phrase.replace('<him-%d>' % (i + 1), participant.accusative())
            phrase = phrase.replace('<he-%d>' % (i + 1), participant.pronoun())
            i = i + 1
        if self.excl:
            phrase = phrase + '!'
        else:
            phrase = phrase + '.'
        return phrase[0].upper() + phrase[1:]


class EventCollector(object):
    def __init__(self):
        self.events = []
    
    def collect(self, event):
        self.events.append(event)


class Oblivion(EventCollector):
    def collect(self, event):
        pass


oblivion = Oblivion()


# 'diction engine' -- almost exactly like a peephole optimizer -- convert
#   "Bob went to the shed.  Bob saw Alice." into
#   "Bob went to the shed, where he saw Alice."
# btw, we currently get a new editor for every paragraph
class Editor(object):
    """The Editor is remarkably similar to the _peephole optimizer_ in
    compiler construction.  Instead of replacing sequences of instructions
    with more efficient but semantically equivalent sequences of
    instructions, it replaces sequences of sentences with more readable
    but semantically equivalent sequences of sentences.

    """
    MEMORY = 1

    def __init__(self):
        self.character = None
        self.character_location = {}
        self.events = []

    def read(self, event):
        if len(self.events) < Editor.MEMORY:
            self.events.append(event)
            return
        
        character = event.participants[0]
        # update our idea of their location
        self.character_location[character.name] = character.location
        # todo: check our idea of their location vs where they are,
        # but that won't matter until an editor looks at more than one
        # paragraph anyway

        if character == self.character:  # same character doing stuff        
            if event.phrase.startswith('<1>'):
                event.phrase = '<he-1>' + event.phrase[3:]

            if (self.events[-1].phrase == '<1> made <his-1> way to <2>' and
                event.phrase == '<1> went to <2>'):
                self.events[-1].participants[1] = event.participants[1]
            elif (self.events[-1].phrase == '<1> went to <2>' and
                event.phrase == '<1> went to <2>'):
                self.events[-1].phrase = '<1> made <his-1> way to <2>'
                self.events[-1].participants[1] = event.participants[1]
            elif (self.events[-1].phrase == '<he-1> made <his-1> way to <2>' and
                event.phrase == '<he-1> went to <2>'):
                self.events[-1].participants[1] = event.participants[1]
            elif (self.events[-1].phrase == '<he-1> went to <2>' and
                event.phrase == '<he-1> went to <2>'):
                self.events[-1].phrase = '<he-1> made <his-1> way to <2>'
                self.events[-1].participants[1] = event.participants[1]
            else:
                self.events.append(event)
        else:  # new character doing stuff
            self.character = character
            self.events.append(event)


### OBJECTS ###

class Actor(object):
    def __init__(self, name, location, collector=None):
        self.name = name
        self.collector = collector
        self.location = None
        self.contents = []
        self.enter = ""
        self.location = None
        if location is not None:
            self.move_to(location)

    def notable(self):
        return False
    
    def treasure(self):  # impies notable usually
        return False

    def horror(self):  # impies notable usually
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

    def emit(self, *args, **kwargs):
        if self.collector:
            self.collector.collect(Event(*args, **kwargs))

    # if self.location is None, this is just an initial move
    def move_to(self, location):
        if self.location:
            self.location.contents.remove(self)
        self.location = location
        self.location.contents.append(self)

    def __str__(self):
        article = self.article()
        if not article:
            return self.name
        return '%s %s' % (article, self.name)

    def indefinite(self):
        article = 'a'
        if self.name.startswith(('a', 'e', 'i', 'o', 'u')):
            article = 'an'
        return '%s %s' % (article, self.name)


class Location(Actor):
    def __init__(self, name, enter="went to"):
        self.name = name
        self.enter = enter
        self.contents = []
        self.exits = []

    def set_exits(self, *exits):
        self.exits = exits


class ProperLocation(Location):
    def article(self):
        return ''

    def posessive(self):
        return "its"

    def accusative(self):
        return "it"


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


class ThreatGiveMeTopic(Topic):
    pass


class ThreatTellMeTopic(Topic):
    pass


class Memory(object):
    def __init__(self, subject, location, i_hid_it_there=False):
        self.subject = subject  # the thing being remembered
        self.location = location  # where we last remember seeing it
        self.i_hid_it_there = i_hid_it_there


class Animate(Actor):
    def __init__(self, name, location, collector=None):
        Actor.__init__(self, name, location, collector=None)
        self.topic = None
        # hash of subject's name to a Memory object
        self.memory = {}

    def animate(self):
        return True

    def notable(self):
        return True

    def address(self, other, topic, phrase, participants=None):
        if participants is None:
            participants = [self, other]
        other.topic = topic
        self.emit(phrase, participants)
        # kind of a hack!
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
        self.emit("<1> was in <2>", [self, self.location])
        for x in self.location.contents:
            if x == self:
                continue
            if x.notable():
                self.emit("<1> saw <2>", [self, x])
                self.memory[x.name] = Memory(x, self.location)


    def move_to(self, location):
        assert(location != self.location)
        assert(location is not None)
        for x in self.location.contents:
            # otherwise we get "Bob saw Bob leave the room", eh?
            if x is self:
                continue
            if x.animate():
                x.emit("<1> saw <2> leave the room", [x, self])
        if self.location is not None:
            self.location.contents.remove(self)
        self.location = location
        self.location.contents.append(self)
        self.emit("<1> went to <2>", [self, self.location])
        if random.randint(0, 10) == 0:
            self.emit("It was so nice being in <2> again",
             [self, self.location], excl=True)
        
        # am I carrying the revolver?
        revolver = None
        for z in self.contents:
            if z.name == 'revolver':
                revolver = z
                break

        for x in self.location.contents:
            if x == self:
                continue
            if x.horror():
                memory = self.memory.get(x.name, None)
                if memory:
                    amount = pick(['shudder', 'wave'])
                    emotion = pick(['fear', 'disgust', 'sickness'])
                    self.emit("<1> felt a %s of %s as <he-1> looked at <2>" % (amount, emotion), [self, x])
                    self.memory[x.name] = Memory(x, self.location)
                else:
                    verb = pick(['screamed', 'yelped', 'went pale'])
                    self.emit("<1> %s at the sight of <indef-2>" % verb, [self, x], excl=True)
                    self.memory[x.name] = Memory(x, self.location)
            elif x.animate():
                other = x
                self.emit("<1> saw <2>", [self, other])
                other.emit("<1> saw <2> walk into the room", [other, self])
                self.memory[x.name] = Memory(x, self.location)
                self.greet(x, "'Hello, <2>,' said <1>")
                for y in other.contents:
                    if y.treasure():
                        self.emit(
                            "<1> noticed <2> was carrying <indef-3>",
                            [self, other, y])
                        if revolver:
                            # this should be a ThreatTopic, below should
                            # be a RequestTopic -- er no, maybe not, but
                            # it would be nice if there was some way to
                            # indicate the revolver as part of the Topic
                            self.emit("<1> pointed <3> at <2>",
                                [self, other, revolver])
                            other.memory[revolver.name] = Memory(revolver, self)
                            # for comic relief!
                            #if random.randint(0, 4) == 0:
                            #    y = pick(ALL_ITEMS)
                            self.address(other,
                                ThreatGiveMeTopic(self, subject=y),
                                "'Please give me <3>, <2>, or I shall shoot you,' <he-1> said",
                                [self, other, y])
                            return
                # another case of mind-reading.  well, it helps the story advance!
                # (it would help more to double-check this against your OWN memory)
                if revolver:
                    for key in other.memory:
                        memory = other.memory[key]
                        self_memory = self.memory.get(key)
                        if self_memory and self_memory.i_hid_it_there:
                            continue
                        if memory.i_hid_it_there and memory.subject.name != 'revolver':
                            y = memory.subject
                            self.emit("<1> pointed <3> at <2>",
                                [self, other, revolver])
                            other.memory[revolver.name] = Memory(revolver, self)
                            # for comic relief!
                            #if random.randint(0, 4) == 0:
                            #    y = pick(ALL_ITEMS)
                            self.address(other,
                                ThreatTellMeTopic(self, subject=y),
                                "'Tell me where you have hidden <3>, <2>, or I shall shoot you,' <he-1> said",
                                [self, other, y])
                            return
            elif x.notable():
                self.emit("<1> saw <2>", [self, x])
                self.memory[x.name] = Memory(x, self.location)

    def live(self):
        # first, if in a conversation, turn total attention to that
        if self.topic is not None:
            return self.converse(self.topic)

        # otherwise, if there are valuable items here, you *must* pick them up.
        for x in self.location.contents:
            if x.notable() and x.takeable():
                self.emit("<1> picked up <2>", [self, x])
                x.move_to(self)
                self.memory[x.name] = Memory(x, self)
                return
        people_about = False

        # otherwise, fixate on some valuable object (possibly the revolver)
        # that you are carrying:
        treasure = None
        for y in self.contents:
            if y.treasure():
                treasure = y
                break
        if not treasure and random.randint(0, 20) == 0:
            for y in self.contents:
                if y.name == 'revolver':
                    treasure = y
                    break

        # check if you are alone
        for x in self.location.contents:
            if x.animate() and x is not self:
                people_about = True

        # check for some place to hide the thing you're fixating on
        for x in self.location.contents:
            if x.container() and not people_about and treasure:
                self.emit("<1> hid <2> in <3>", [self, y, x])
                y.move_to(x)
                self.memory[y.name] = Memory(y, x, i_hid_it_there=True)
                return self.wander()
            if x.container() and not people_about:
                # did I hide something here previously?
                memory = None
                for key in self.memory:
                    if self.memory[key].location == x and self.memory[key].i_hid_it_there:
                        memory = self.memory[key]
                        break
                if memory and memory.subject.name == 'revolver':
                    y = memory.subject
                    self.emit("<1> retrieved <3> from <2>",
                              [self, x, y])
                    if y.location != x:
                        self.emit("But it was missing", [self], excl=True)
                        # forget ALLLLLLL about it, then.  so realistic!
                        del self.memory[y.name]
                    else:
                        memory.subject.move_to(self)
                        self.memory[y.name] = Memory(memory.subject, self)
                if memory:
                    self.emit("<1> checked that <3> was still in <2>",
                              [self, x, memory.subject])
                    if memory.subject.location != x:
                        self.emit("But it was missing", [self], excl=True)
                        del self.memory[memory.subject.name]
                elif random.randint(0, 2) == 0:
                    self.emit("<1> searched <2>", [self, x])
                    for y in x.contents:
                        if y.notable() and y.takeable():
                            self.emit("<1> found <2> hidden there, and took <him-2>", [self, y])
                            y.move_to(self)
                            self.memory[y.name] = Memory(y, self)
        if random.randint(0, 8) == 0:
            which = random.randint(0, 5)
            if which == 0:
                self.emit("<1> yawned", [self])
            if which == 1:
                self.emit("<1> gazed thoughtfully into the distance", [self])
            if which == 2:
                self.emit("<1> thought <he-1> heard something", [self])
            if which == 3:
                self.emit("<1> scratched <his-1> head", [self])
            if which == 4:
                self.emit("<1> immediately had a feeling something was amiss", [self])
        else:
            return self.wander()

    def converse(self, topic):
        self.topic = None
        other = topic.originator
        if isinstance(topic, ThreatGiveMeTopic):
            found_object = None
            for x in self.contents:
                if x is topic.subject:
                    found_object = x
                    break
            if not found_object:
                self.speak_to(other,
                    "'But I don't have <3>!' protested <1>",
                    [self, other, topic.subject])
            else:
                self.speak_to(other,
                    "'Please don't shoot!', <1> cried, and handed over <3>",
                    [self, other, found_object])
                found_object.move_to(other)
        elif isinstance(topic, ThreatTellMeTopic):
            memory = self.memory.get(topic.subject.name)
            if not memory:
                self.speak_to(other,
                    "'I have no memory of that, <2>,' <1> replied",
                    [self, other, topic.subject])
            else:
                self.speak_to(other,
                    "'Please don't shoot!', <1> cried, 'It's in <3>'",
                    [self, other, memory.location])
                other.memory[topic.subject.name] = \
                  Memory(topic.subject, memory.location)
        elif isinstance(topic, GreetTopic):
            # emit, because making this a speak_to leads to too much silliness
            self.emit("'Hello, <2>,' replied <1>", [self, other])
            # but otoh this sort of thing does not scale:
            other.emit("'Hello, <2>,' replied <1>", [self, other])
            # this needs to be more general
            self_memory = self.memory.get('dead body')
            # in general, characters should not be able to read each other's
            # minds.  however, it's convenient here.  besides, their face would
            # be pretty easy to read in this circumstance.
            other_memory = other.memory.get('dead body')
            if self_memory and not other_memory:
                self.question(other,
                   "'Did you know there's <indef-3> in <4>?' asked <1> quickly",
                   [self, other, self_memory.subject, self_memory.location],
                   subject=self_memory.subject)
                return
            # this needs to be not *all* the time
            for x in other.contents:
                if x.notable():
                    self.memory[x.name] = Memory(x, other)
                    self.speak_to(other, "'I see you are carrying <indef-3>,' said <1>", [self, other, x])
                    return
            choice = random.randint(0, 3)
            if choice == 0:
                self.question(other, "'Lovely weather we're having, isn't it?' asked <1>")
            if choice == 1:
                self.speak_to(other, "'I was wondering where you were,' said <1>")
        elif isinstance(topic, QuestionTopic):
            if topic.subject is not None:
                choice = random.randint(0, 1)
                if choice == 0:
                    self.speak_to(other, "'I know nothing about <3>, <2>,' explained <1>",
                       [self, other, topic.subject])
                if choice == 1:
                    self.speak_to(other, "'Perhaps, <2>,' replied <1>")
            else:
                self.speak_to(other, "'Perhaps, <2>,' replied <1>")
        elif isinstance(topic, SpeechTopic):
            choice = random.randint(0, 5)
            if choice == 0:
                self.emit("<1> nodded", [self])
            if choice == 1:
                self.emit("<1> remained silent", [self])
            if choice == 2:
                self.question(other, "'Do you really think so?' asked <1>")
            if choice == 3:
                self.speak_to(other, "'Yes, it's a shame really,' stated <1>")
            if choice == 4:
                self.speak_to(other, "'Oh, I know, I know,' said <1>")
            if choice == 5:
                item = pick(ALL_ITEMS)
                self.question(other, "'But what about <3>, <2>?' posed <1>",
                    [self, other, item], subject=item)

    def wander(self):
        self.move_to(
            self.location.exits[
                random.randint(0, len(self.location.exits)-1)
            ]
        )


class Item(Actor):
    def takeable(self):
        return True

    def notable(self):
        return True
            


class Male(Animate):
    def article(self):
        return ''

    def posessive(self):
        return "his"

    def accusative(self):
        return "him"

    def pronoun(self):
        return "he"


class Female(Animate):
    def article(self):
        return ''

    def posessive(self):
        return "her"

    def accusative(self):
        return "her"

    def pronoun(self):
        return "she"


class Container(Actor):
    def container(self):
        return True


class Treasure(Item):
    def treasure(self):
        return True


# TODO Plural should really be a mixin.
class PluralTreasure(Treasure):
    def article(self):
        return 'the'

    def posessive(self):
        return "their"

    def accusative(self):
        return "them"

    def pronoun(self):
        return "they"

    def indefinite(self):
        article = 'some'
        return '%s %s' % (article, self.name)


class Horror(Actor):
    def notable(self):
        return True

    def horror(self):
        return True


### world ###

kitchen = Location('kitchen')
living_room = Location('living room')
dining_room = Location('dining room')
front_hall = Location('front hall')
driveway = Location('driveway')
garage = Location('garage')
path_by_the_shed = Location('path by the shed')
shed = Location('shed')
upstairs_hall = Location('upstairs hall')
study = Location('study')
bathroom = Location('bathroom')
bobs_bedroom = ProperLocation("Bob's bedroom")
alices_bedroom = ProperLocation("Alice's bedroom")

kitchen.set_exits(dining_room, front_hall)
living_room.set_exits(dining_room, front_hall)
dining_room.set_exits(living_room, kitchen)
front_hall.set_exits(kitchen, living_room, driveway, upstairs_hall)
driveway.set_exits(front_hall, garage, path_by_the_shed)
garage.set_exits(driveway)
path_by_the_shed.set_exits(driveway, shed)
shed.set_exits(path_by_the_shed)
upstairs_hall.set_exits(bobs_bedroom, alices_bedroom, front_hall, study, bathroom)
bobs_bedroom.set_exits(upstairs_hall)
alices_bedroom.set_exits(upstairs_hall)
study.set_exits(upstairs_hall)
bathroom.set_exits(upstairs_hall)

house = (kitchen, living_room, dining_room, front_hall, driveway, garage,
         upstairs_hall, bobs_bedroom, alices_bedroom, study, bathroom,
         path_by_the_shed, shed)

falcon = Treasure('golden falcon', dining_room)
jewels = PluralTreasure('stolen jewels', garage)

cupboards = Container('cupboards', kitchen)
cabinet = Container('cabinet', dining_room)
mailbox = Container('mailbox', driveway)

bobs_bed = Container("bed", bobs_bedroom)
alices_bed = Container("bed", alices_bedroom)

revolver = Item('revolver', pick([bobs_bed, alices_bed]))
dead_body = Horror('dead body', bathroom)

alice = Female('Alice', None)
bob = Male('Bob', None)

ALL_ITEMS.extend([falcon, jewels, revolver])

### main ###

friffery = False
debug = False

print "Swallows and Sorrows (DRAFT)"
print "============================"
print

for chapter in range(1, 17):
    print "Chapter %d." % chapter
    print "-----------"
    print

    alice_collector = EventCollector()
    bob_collector = EventCollector()
    # don't continue a conversation from the previous chapter, please
    alice.topic = None
    bob.topic = None
    alice.location = None
    bob.location = None

    for paragraph in range(1, 26):
        alice.collector = alice_collector
        bob.collector = bob_collector
        
        # we could do this randomly...
        #pov_actor = pick([alice, bob])
        # but, we could also alternate.  They ARE Alice and Bob, after all.
        pov_actor = (alice, bob)[(paragraph - 1) % 2]

        for actor in (alice, bob):
            if actor.location is None:
                actor.place_in(pick(house))
            else:
                # this is hacky & won't work for >2 characters:
                if not (alice.location == bob.location):
                    actor.emit("<1> was in <2>", [actor, actor.location])

        while len(pov_actor.collector.events) < 20:
            alice.live()
            bob.live()

        if friffery:
            if paragraph == 1:
                choice = random.randint(0, 3)
                if choice == 0:
                    sys.stdout.write("It was raining.  ")
                if choice == 1:
                    sys.stdout.write("It was snowing.  ")
                if choice == 2:
                    sys.stdout.write("The sun was shining.  ")
                if choice == 3:
                    sys.stdout.write("The day was overcast and humid.  ")
            elif not str(c.events[0]).startswith("'"):
                choice = random.randint(0, 8)
                if choice == 0:
                    sys.stdout.write("Later on, ")
                if choice == 1:
                    sys.stdout.write("Suddenly, ")
                if choice == 2:
                    sys.stdout.write("After a moment's consideration, ")
                if choice == 3:
                    sys.stdout.write("Feeling anxious, ")

        if debug:
            print "ALICE'S POV:"
            for event in alice_collector.events:
                print str(event)
            print
            print "BOB'S POV:"
            for event in bob_collector.events:
                print str(event)
            print
            print "- - - - -"
            print

        if not debug:
            editor = Editor()
            for event in pov_actor.collector.events:
                editor.read(event)
            for event in editor.events:
                sys.stdout.write(str(event) + "  ")
                #sys.stdout.write("\n")
            print
            print

        alice_collector.events = []
        bob_collector.events = []

