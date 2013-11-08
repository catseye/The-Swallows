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
