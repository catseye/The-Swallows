#!/usr/bin/env python

import random
import sys

from swallows.util import pick

# TODO

# Diction:
# the event-accumulation framework could use rewriting at some point.
# eliminate identical duplicate sentences
# Bob is in the dining room & "Bob made his way to the dining room" ->
#  "Bob wandered around for a bit, then came back to the dining room"
# a better solution for "Bob was in the kitchen" at the start of a paragraph;
#   this might include significant memories Bob acquired in the last
#   paragraph -- such as finding a revolver in the bed
# paragraphs should not always be the same number of events.  variety!
# the Editor should take all the events in the chapter, and decide where
#   paragraph breaks should go.  this is difficult, because syncing up
#   Bob's and Alice's events.  timestamps?
# at least, the Editor should record "rich events", which include information
#   about the main (acting) character, and where the audience last saw them
# use indef art when they have no memory of an item that they see
# dramatic irony would be really nice, but hard to pull off.  Well, a certain
#  amount happens naturally now, with character pov.  but more could be done
# "Chapter 3.  _In which Bob hides the stolen jewels in the mailbox, etc_" --
#  i.e. chapter summaries -- that's a little too fancy to hope for, but with
#  a sufficiently smart Editor it could be done

### EVENTS ###

class Event(object):
    def __init__(self, phrase, participants, excl=False):
        """participants[0] is always the initiator, and we
        record the location that the event was initiated in.

        For now, we assume such an event can be:
        - observed by every actor at that location
        - affects only actors at that location

        In the future, we *may* have:
        - active and passive participants
        - active participants all must be present at the location
        - passive participants need not be

        """
        self.phrase = phrase
        self.participants = participants
        self.location = participants[0].location
        self.excl = excl

    def initiator(self):
        return self.participants[0]

    def __str__(self):
        phrase = self.phrase
        i = 0
        for participant in self.participants:
            phrase = phrase.replace('<%d>' % (i + 1), participant.render(self.participants))
            phrase = phrase.replace('<indef-%d>' % (i + 1), participant.indefinite())
            phrase = phrase.replace('<his-%d>' % (i + 1), participant.posessive())
            phrase = phrase.replace('<him-%d>' % (i + 1), participant.accusative())
            phrase = phrase.replace('<he-%d>' % (i + 1), participant.pronoun())
            phrase = phrase.replace('<was-%d>' % (i + 1), participant.was())
            phrase = phrase.replace('<is-%d>' % (i + 1), participant.is_())
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
class LegacyEditor(object):
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
        if len(self.events) < self.__class__.MEMORY:
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


class LegacyPublisher(object):
    """Publisher which uses the old Event/Editor framework.

    Will probably go away eventually, but nice to have as a reference
    while working on the new Event/Editor framework.

    """
    def __init__(self, **kwargs):
        self.alice = kwargs.get('alice')
        self.bob = kwargs.get('bob')
        self.house = kwargs.get('house')
        self.friffery = kwargs.get('friffery', False)
        self.debug = kwargs.get('debug', False)
        self.title = kwargs.get('title', "Untitled")
        self.chapters = kwargs.get('chapters', 16)
        self.paragraphs_per_chapter = kwargs.get('paragraphs_per_chapter', 25)

    def publish(self):
        print self.title
        print "=" * len(self.title)
        print

        alice = self.alice
        bob = self.bob
        house = self.house

        for chapter in range(1, self.chapters+1):
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
        
            for paragraph in range(1, self.paragraphs_per_chapter+1):
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
        
                actor_order = (alice, bob)
                # this leads to continuity problems:
                #if random.randint(0, 1) == 0:
                #    actor_order = (bob, alice)
                while len(pov_actor.collector.events) < 20:
                    for actor in actor_order:
                        actor.live()
        
                if self.friffery:
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
        
                if self.debug:
                    print "ALICE'S POV:"
                    for event in alice_collector.events:
                        print str(event)
                    print
                    alice.dump_memory()
                    print
                    print "BOB'S POV:"
                    for event in bob_collector.events:
                        print str(event)
                    print
                    bob.dump_memory()
                    print
                    print "- - - - -"
                    print
        
                if not self.debug:
                    editor = LegacyEditor()
                    for event in pov_actor.collector.events:
                        editor.read(event)
                    for event in editor.events:
                        sys.stdout.write(str(event) + "  ")
                        #sys.stdout.write("\n")
                    print
                    print
        
                alice_collector.events = []
                bob_collector.events = []
