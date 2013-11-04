#!/usr/bin/env python

#
# the_swallows.py: a novel generator.
# Chris Pressey, Cat's Eye Technologies
#

import random
import sys

# TODO
# "in which bob hides the stolen jewels in the mailbox"
# "where have you hidden the jewels?"
# more reacting to the dead body:
# - calling the police
# - trying to dispose of it
# an unspeakable thing in the basement!
# 'diction engine' -- almost exactly like a peephole optimizer -- convert
#   "Bob went to the shed.  Bob saw Alice." into
#   "Bob went to the shed, where he saw Alice."
# Alice shouldn't always move first
# paragraphs should not always be the same number of events.  variety!
# path-finder between any two rooms -- not too difficult, even if it
#   would be nicer in Prolog.
# DRAMATIC IRONY would be really nice, but hard to pull off.

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
        return phrase


class EventCollector(object):
    def __init__(self):
        self.events = []
    
    def collect(self, event):
        self.events.append(event)


class Oblivion(EventCollector):
    def collect(self, event):
        pass

oblivion = Oblivion()

### OBJECTS ###

class Actor(object):
    def __init__(self, name, location, collector=None):
        self.name = name
        self.collector = collector
        self.location = None
        self.contents = []
        self.enter = ""
        self.move_to(location, initial=True)

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

    def move_to(self, location, initial=False):
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


class ThreatTopic(Topic):
    pass


class Memory(object):
    def __init__(self, subject, location):
        self.subject = subject
        self.location = location


class Animate(Actor):
    def __init__(self, name, location, collector=None):
        Actor.__init__(self, name, location, collector=None)
        self.topic = None
        # hash of actor's name to a Memory object
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

    def greet(self, other, phrase, participants=None):
        self.address(other, GreetTopic(self), phrase, participants)

    def speak_to(self, other, phrase, participants=None, subject=None):
        self.address(other, SpeechTopic(self, subject=subject), phrase, participants)

    def question(self, other, phrase, participants=None, subject=None):
        self.address(other, QuestionTopic(self, subject=subject), phrase, participants)

    def threaten(self, other, phrase, participants=None, subject=None):
        self.address(other, ThreatTopic(self, subject=subject), phrase, participants)

    def move_to(self, location, initial=False):
        if self.location:
            self.location.contents.remove(self)
        self.location = location
        self.location.contents.append(self)
        if initial:
            self.emit("<1> was in <2>", [self, self.location])
        else:
            verb = pick(['went to', 'walked to', 'moved to'])
            self.emit("<1> %s <2>" % verb, [self, self.location])
        if random.randint(0, 10) == 0:
            self.emit("It was so nice being in <2> again",
             [self, self.location], excl=True)
        for x in self.location.contents:
            if x == self:
                continue
            if x.horror():
                memory = self.memory.get(x.name, None)
                if memory:
                    amount = pick(['shudder', 'wave', 'uprising'])
                    emotion = pick(['fear', 'disgust', 'nausea', 'uneasiness'])
                    self.emit("<1> felt a %s of %s as <he-1> looked at <2>" % (amount, emotion), [self, x])
                    self.memory[x.name] = Memory(x, self.location)
                else:
                    verb = pick(['screamed', 'yelped', 'went pale'])
                    self.emit("<1> %s at the sight of <indef-2>" % verb, [self, x], excl=True)
                    self.memory[x.name] = Memory(x, self.location)
            elif x.animate():
                other = x
                self.emit("<1> saw <2>", [self, other])
                self.memory[x.name] = Memory(x, self.location)
                self.greet(x, "'Hello, <2>,' said <1>")
                for y in other.contents:
                    if y.treasure():
                        self.emit(
                            "<1> noticed <2> was carrying <indef-3>",
                            [self, other, y])
                        revolver = None
                        for z in self.contents:
                            if z.name == 'revolver':
                                revolver = z
                                break
                        if revolver:
                            # this should be a ThreatTopic, below should
                            # be a RequestTopic
                            self.emit("<1> pointed <3> at <2>",
                                [self, other, revolver])
                            # for comic relief!
                            if random.randint(0, 4) == 0:
                                y = pick(ALL_ITEMS)
                            self.threaten(other,
                                "'Please give me <3>, <2>, or I shall shoot you,' <he-1> said",
                                [self, other, y],
                                subject=y)
                            return
            elif x.notable():
                self.emit("<1> saw <2>", [self, x])
                self.memory[x.name] = Memory(x, self.location)

    def live(self):
        if self.topic is not None:
            return self.converse(self.topic)
        for x in self.location.contents:
            if x.notable() and x.takeable():
                self.emit("<1> picked up <2>", [self, x])
                x.move_to(self)
                return
        people_about = False

        # what the character is aware they're carrying; occasionally = gun
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

        for x in self.location.contents:
            if x.animate() and x is not self:
                people_about = True
        for x in self.location.contents:
            if x.container() and not people_about and treasure:
                self.emit("<1> hid <2> in <3>", [self, y, x])
                y.move_to(x)
                return self.wander()
            if x.container() and not people_about and random.randint(0, 2) == 0:
                self.emit("<1> examined <2> carefully", [self, x])
                for y in x.contents:
                    if y.notable() and y.takeable():
                        self.emit("<1> found <2> hidden there, and took <him-2>", [self, y])
                        y.move_to(self)
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
        if isinstance(topic, ThreatTopic):
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
        elif isinstance(topic, GreetTopic):
            # emit, because making this a speak_to leads to too much silliness
            self.emit("'Hello, <2>,' replied <1>", [self, other])
            # this needs to be more general
            memory = self.memory.get('dead body')
            if memory:
                self.question(other,
                   "'Did you know there's <indef-3> in <4>?' asked <1> quickly",
                   [self, other, memory.subject, memory.location],
                   subject=memory.subject)
                return
            # this needs to be not *all* the time
            for x in other.contents:
                if x.notable():
                    self.speak_to(other, "'I see you are carrying <indef-3>,' said <1>", [self, other, x])
                    return
            choice = random.randint(0, 3)
            if choice == 0:
                self.question(other, "'Lovely weather we're having, isn't it?' asked <1>")
            if choice == 1:
                self.speak_to(other, "'I was wondering where you were.' said <1>")
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

alice = Female('Alice', kitchen)
bob = Male('Bob', living_room)

ALL_ITEMS.extend([falcon, jewels, revolver])

### main ###

print "Swallows and Sorrows (DRAFT)"
print "============================"
print

for chapter in range(1, 16):
    print "Chapter %d." % chapter
    print "-----------"
    print

    c = EventCollector()
    alice.collector = c
    bob.collector = c
    alice.move_to(pick(house), initial=True)
    bob.move_to(pick(house), initial=True)
    # don't continue a conversation from the previous chapter, please
    alice.topic = None
    bob.topic = None

    for paragraph in range(1, 30):
        while len(c.events) < 20:
            alice.live()
            bob.live()

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

        for event in c.events:
          sys.stdout.write(str(event) + "  ")
          #sys.stdout.write("\n")
        print
        print
        c.events = []

