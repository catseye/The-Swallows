#!/usr/bin/env python

import random
import sys

from swallows.util import pick

# TODO

# Diction:
# - eliminate identical duplicate sentences
# - Bob is in the dining room & "Bob made his way to the dining room" ->
#   "Bob wandered around for a bit, then came back to the dining room"
# - comvert "Bob went to the shed.  Bob saw Alice." into
#           "Bob went to the shed, where he saw Alice."
# - a better solution for "Bob was in the kitchen" at the start of a paragraph;
#   this might include significant memories Bob acquired in the last
#   paragraph -- such as finding a revolver in the bed
# - use indef art when they have no memory of an item that they see
# - dramatic irony would be really nice, but hard to pull off.  Well, a certain
#   amount happens naturally now, with character pov.  but more could be done
# - "Chapter 3.  _In which Bob hides the stolen jewels in the mailbox, etc_" --
#   i.e. chapter summaries -- that's a little too fancy to hope for, but with
#   a sufficiently smart Editor it could be done

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
        (probably done by passing a number n: the first n
        participants are to be considered active)

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

    def dedup(self):
        """Modifies the sequence of events so that the same event
        does not occur multiple times in a row.

        """
        if len(self.events) <= 1:
            return
        events = [self.events[0]]
        for event in self.events[1:]:
            if str(event) != str(events[-1]):
                events.append(event)
        self.events = events
        

# not really needed, as emit() does nothing if there is no collector
class Oblivion(EventCollector):
    def collect(self, event):
        pass


oblivion = Oblivion()


### the new stuff ###


class Editor(object):
    """The Editor is remarkably similar to the _peephole optimizer_ in
    compiler construction.  Instead of replacing sequences of instructions
    with more efficient but semantically equivalent sequences of
    instructions, it replaces sequences of sentences with more readable
    but semantically equivalent sequences of sentences.

    The Editor is also responsible for chopping up the sequence of
    sentences into "sensible" paragraphs.  (This might be like a compiler
    code-rewriting pass that inserts NOPs to ensure instructions are on a
    word boundary, or some such.)
    
    The Editor is also responsible for picking which character to
    follow.  (I don't think there's a compiler construction analogy for
    that.)

    """
 
    def __init__(self, collector, main_characters):
        self.events = list(reversed(collector.events))
        self.main_characters = main_characters
        self.pov_index = 0
        # maps main characters to where they last were (omniscient)
        self.character_location = {}
        # maps main characters to where the reader last saw them
        self.last_seen_at = {}        

    def publish(self):
        while len(self.events) > 0:
            pov_actor = self.main_characters[self.pov_index]
            paragraph_events = self.generate_paragraph_events(pov_actor)
            self.publish_paragraph(paragraph_events)
            self.pov_index += 1
            if self.pov_index >= len(self.main_characters):
                self.pov_index = 0

    def generate_paragraph_events(self, pov_actor):
        quota = random.randint(10, 25)
        paragraph_events = []
        while len(paragraph_events) < quota and len(self.events) > 0:
            consume_another_event = True
            while consume_another_event and len(self.events) > 0:
                consume_another_event = False
                event = self.events.pop()

                # optimize
                if paragraph_events:
                    last_character = paragraph_events[-1].participants[0]
                    if event.participants[0] == last_character:
                        # replace repeated proper nouns with pronouns
                        if event.phrase.startswith('<1>'):
                            event.phrase = '<he-1>' + event.phrase[3:]

                        # replace chains of 'went to' with 'made way to'
                        if (paragraph_events[-1].phrase in ('<1> went to <2>', '<he-1> went to <2>') and
                             event.phrase == '<he-1> went to <2>'):
                             assert event.location == event.participants[1]
                             assert paragraph_events[-1].location == paragraph_events[-1].participants[1]
                             paragraph_events[-1].phrase = '<1> made <his-1> way to <2>'
                             paragraph_events[-1].participants[1] = event.participants[1]
                             paragraph_events[-1].location = event.participants[1]
                             # ack
                             paragraph_events[-1].original_location = self.character_location[last_character]
                             consume_another_event = True
                        elif (paragraph_events[-1].phrase in ('<1> made <his-1> way to <2>', '<he-1> made <his-1> way to <2>') and
                             event.phrase == '<he-1> went to <2>'):
                             assert event.location == event.participants[1]
                             assert paragraph_events[-1].location == paragraph_events[-1].participants[1]
                             paragraph_events[-1].phrase = '<1> made <his-1> way to <2>'
                             paragraph_events[-1].participants[1] = event.participants[1]
                             paragraph_events[-1].location = event.participants[1]
                             
                             # and if they 'made their way' to their current location...
                             # if self.character_location[last_character] == paragraph_events[-1].original_location:
                             #     paragraph_events[-1].phrase = '<1> wandered around for a bit, then went back to <2>'
                                 
                             consume_another_event = True

            if not paragraph_events:
                # this is the first sentence of the paragraph
                # if the reader wasn't aware they were here, add an event
                if self.last_seen_at.get(pov_actor, None) != event.location:
                    if not (('went to' in event.phrase) or ('made <his-1> way to' in event.phrase) or (event.phrase == '<1> was in <2>')):
                        paragraph_events.append(Event('<1> was in <2>', [pov_actor, event.location]))

            # update our idea of where the character is, even if these are
            # not events we will be dumping out
            self.character_location[event.participants[0]] = event.location

            if event.location == self.character_location[pov_actor]:
                paragraph_events.append(event)
                # update the reader's idea of where the character is
                self.last_seen_at[event.participants[0]] = event.location

        return paragraph_events

    def publish_paragraph(self, paragraph_events):
        for event in paragraph_events:
            sys.stdout.write(str(event) + "  ")
            #sys.stdout.write("\n")
        print
        print


class Publisher(object):
    def __init__(self, **kwargs):
        self.characters = kwargs.get('characters')
        self.setting = kwargs.get('setting')
        self.friffery = kwargs.get('friffery', False)
        self.debug = kwargs.get('debug', False)
        self.title = kwargs.get('title', "Untitled")
        self.chapters = kwargs.get('chapters', 18)
        self.events_per_chapter = kwargs.get('events_per_chapter', 810)

    def publish_chapter(self, chapter_num):
        collector = EventCollector()
        
        for actor in self.characters:
            actor.collector = collector
            # don't continue a conversation from the previous chapter, please
            actor.topic = None
            actor.place_in(pick(self.setting))

        while len(collector.events) < self.events_per_chapter:
            for actor in self.characters:
                actor.live()
                #print len(collector.events) # , repr([str(e) for e in collector.events])

        # this contains duplicates because we are producing duplicates in
        # the engine because the engine assumes each actor has its own
        # event collector which is no longer the case.
        # This dedup'ing is temporary.
        # Eventually, we will dedup at the source (the Actors which
        # are currently producing redundant events.)
        collector.dedup()

        if self.debug:
            for character in self.characters:
                print "%s'S EVENTS:" % character.name.upper()                
                for event in collector.events:
                    if event.participants[0] != character:
                        continue
                    print "%r in %s: %s" % (
                        [p.render([]) for p in event.participants],
                        event.location.render([]),
                        event.phrase
                    )
                print
            for character in self.characters:
                print "%s'S STATE:" % character.name.upper()
                character.dump_memory()
                print
            print "- - - - -"
            print

        editor = Editor(collector, self.characters)
        editor.publish()

    def publish(self):
        print self.title
        print "=" * len(self.title)
        print

        for chapter in range(1, self.chapters+1):
            print "Chapter %d." % chapter
            print "-----------"
            print

            self.publish_chapter(chapter)
