#!/usr/bin/env python

import random
import sys

# TODO

# Diction:
# - Bob is in the dining room & "Bob made his way to the dining room" ->
#   "Bob wandered around for a bit, then came back to the dining room"
# - convert "Bob went to the shed.  Bob saw Alice." into
#           "Bob went to the shed, where he saw Alice."
#   ...this is trickier than it looks because <1> is Bob, <2> is shed, and
#   Alice was <2> but now she has to become <3>, or... something.
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

    def rephrase(self, new_phrase):
        """Does not modify the event.  Returns a new copy."""
        return Event(new_phrase, self.participants, excl=self.excl)

    def initiator(self):
        return self.participants[0]

    def render(self):
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
        return phrase

    def __str__(self):
        phrase = self.render()
        if self.excl:
            phrase = phrase + '!'
        else:
            phrase = phrase + '.'
        return phrase[0].upper() + phrase[1:]


class AggregateEvent(Event):
    """Attempt at a way to combine multiple events into a single
    sentence.  Each constituent event must have the same initiator.

    """
    def __init__(self, template, events, excl=False):
        self.template = template
        self.events = events
        self.excl = excl
        self.phrase = 'SEE SUBEVENTS PLZ'
        self._initiator = self.events[0].initiator()
        for event in self.events:
            assert event.initiator() == self._initiator
        self.location = self._initiator.location

    def rephrase(self, new_phrase):
        #raise NotImplementedError
        return self

    def initiator(self):
        return self._initiator

    def __str__(self):
        phrase = self.template % tuple([x.render() for x in self.events])
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


### EDITOR AND PUBLISHER ###

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

    Note that the event stream must start with "<Character> was in <place>"
    as the first event for each character.  Otherwise the Editor don't know
    who started where.

    """
 
    def __init__(self, collector, main_characters):
        self.events = list(reversed(collector.events))
        self.main_characters = main_characters
        self.pov_index = 0
        # maps main characters to where they currently are (omnisciently)
        self.character_location = {}
        # maps main characters to where the reader last saw them
        self.last_seen_at = {}        

    def publish(self):
        while len(self.events) > 0:
            pov_actor = self.main_characters[self.pov_index]
            paragraph_events = self.generate_paragraph_events(pov_actor)
            if paragraph_events:
                paragraph_events = self.optimize_paragraph_events(paragraph_events)
            self.publish_paragraph(paragraph_events)
            self.pov_index += 1
            if self.pov_index >= len(self.main_characters):
                self.pov_index = 0

    def generate_paragraph_events(self, pov_actor):
        quota = random.randint(10, 25)
        paragraph_events = []
        while len(paragraph_events) < quota and len(self.events) > 0:
            event = self.events.pop()

            if not paragraph_events:
                # this is the first sentence of the paragraph
                # if the reader wasn't aware they were here, add an event
                if self.last_seen_at.get(pov_actor, None) != event.location:
                    if not (('went to' in event.phrase) or ('made <his-1> way to' in event.phrase) or (event.phrase == '<1> <was-1> in <2>')):
                        paragraph_events.append(Event('<1> <was-1> in <2>', [pov_actor, event.location]))

            # update our idea of where the character is, even if these are
            # not events we will be dumping out
            self.character_location[event.initiator()] = event.location

            if event.location == self.character_location[pov_actor]:
                paragraph_events.append(event)
                # update the reader's idea of where the character is
                self.last_seen_at[event.initiator()] = event.location

        return paragraph_events

    def optimize_paragraph_events(self, incoming_events):
        incoming_events = list(reversed(incoming_events))
        events = []
        events.append(incoming_events.pop())
        
        def dedup_append(event):
            # check for verbatim repeated. this could be 'dangerous' if, say,
            # you have two characters, Bob Jones and Bob Smith, and both are
            # named 'Bob', and they are actually two different events... but...
            # for now that is an edge case.
            if str(event) == str(events[-1]):
                events[-1].phrase = event.phrase + ', twice'
            elif str(event.rephrase(event.phrase + ', twice')) == str(events[-1]):
                events[-1].phrase = event.phrase + ', several times'
            elif str(event.rephrase(event.phrase + ', several times')) == str(events[-1]):
                pass
            else:
                events.append(event)

        while incoming_events:
            consume_another_event = True
            while consume_another_event and incoming_events:
                consume_another_event = False
                event = incoming_events.pop()
                last_character = events[-1].initiator()
                if event.initiator() == last_character:

                    # replace repeated proper nouns with pronouns
                    if event.phrase.startswith('<1>'):
                        event.phrase = '<he-1>' + event.phrase[3:]
                
                    # replace chains of 'went to' with 'made way to'
                    if (events[-1].phrase in ('<1> went to <2>', '<he-1> went to <2>') and
                         event.phrase == '<he-1> went to <2>'):
                         assert event.location == event.participants[1]
                         assert events[-1].location == events[-1].participants[1]
                         events[-1].phrase = '<1> made <his-1> way to <2>'
                         events[-1].participants[1] = event.participants[1]
                         events[-1].location = event.participants[1]
                         # ack
                         events[-1].original_location = self.character_location[last_character]
                         consume_another_event = True
                    elif (events[-1].phrase in ('<1> made <his-1> way to <2>', '<he-1> made <his-1> way to <2>') and
                         event.phrase == '<he-1> went to <2>'):
                         assert event.location == event.participants[1]
                         assert events[-1].location == events[-1].participants[1]
                         events[-1].phrase = '<1> made <his-1> way to <2>'
                         events[-1].participants[1] = event.participants[1]
                         events[-1].location = event.participants[1]
                         consume_another_event = True
                         
                    # and if they 'made their way' to their current location...
                    # if self.character_location[last_character] == events[-1].original_location:
                    #     events[-1].phrase = '<1> wandered around for a bit, then went back to <2>'

            dedup_append(event)

        return events

    def publish_paragraph(self, paragraph_events):
        for event in paragraph_events:
            sys.stdout.write(str(event) + "  ")
            #sys.stdout.write("\n")
        print
        print


class Publisher(object):
    def __init__(self, characters=(), setting=(), friffery=False,
                 debug=False, title='Untitled', chapters=18,
                 events_per_chapter=810):
        self.characters = characters
        self.setting = setting
        self.friffery = friffery
        self.debug = debug
        self.title = title
        self.chapters = chapters
        self.events_per_chapter = events_per_chapter

    def publish_chapter(self, chapter_num):
        collector = EventCollector()
        
        for character in self.characters:
            character.collector = collector
            # don't continue a conversation from the previous chapter, please
            character.topic = None
            character.place_in(random.choice(self.setting))

        # just testing
        for character in self.characters:
            character.collector.collect(AggregateEvent(
                "%s, then %s",
                [
                  Event("<1> looked at <his-1> shoes", [character]),
                  Event("<1> looked at the sky", [character]),
                ],
                excl=True))

        while len(collector.events) < self.events_per_chapter:
            for character in self.characters:
                character.live()
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
