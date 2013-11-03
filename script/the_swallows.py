#!/usr/bin/env python

import random
import sys

# todo: chapters

class Location:
    def __init__(self, name, enter="went to"):
        self.name = name
        self.article = 'the'
        self.enter = enter
        self.contents = []
        self.exits = []
    
    def set_exits(self, *exits):
        self.exits = exits


kitchen = Location('kitchen')
living_room = Location('living room')
dining_room = Location('dining room')

kitchen.set_exits(dining_room)
living_room.set_exits(dining_room)
dining_room.set_exits(living_room, kitchen)

locations = [kitchen, living_room, dining_room]


class Actor:
    def __init__(self, name, article, location, emit_event=None):
        self.name = name
        self.article = article
        self.emit_event = emit_event
        if not self.emit_event:
            self.emit_event = lambda(x): x
        self.location = None
        self.treasure = False
        self.contents = []
        self.enter = ""
        self.move_to(location)

    def move_to(self, location):
        if self.location:
            self.location.contents.remove(self)
        self.location = location
        self.location.contents.append(self)
        self.emit_event(Event(self, self.location, self.location.enter))
        for x in self.location.contents:
            if x != self:
                self.emit_event(Event(self, x, "saw"))
                for y in x.contents:
                    self.emit_event(Event(self, x, "saw", suffix=" was carrying something"))

    def live(self):
        for x in self.location.contents:
            if x.treasure:
                self.emit_event(Event(self, x, "picked up"))
                x.move_to(self)
        if random.randint(0, 10) == 0:
            self.emit_event(Event(self, None, "yawned"))
        else:
            self.move_to(
                self.location.exits[
                    random.randint(0, len(self.location.exits)-1)
                ]
            )

class Event:
    def __init__(self, subj, obj, verb, suffix=""):
        self.subj = subj
        self.obj = obj
        self.verb = verb
        self.suffix = suffix
    
    def __str__(self):
        if self.obj:
            article = self.obj.article
            if article:
                article += ' '
            return "%s %s %s%s%s." % (
                self.subj.name, self.verb, article, self.obj.name,
                self.suffix
            )
        return "%s %s%s." % (self.subj.name, self.verb, self.suffix)


events = []
def emit_event(e):
    global events
    events.append(e)

alice = Actor('Alice', '', kitchen, emit_event=emit_event)
bob = Actor('Bob', '',living_room, emit_event=emit_event)

falcon = Actor('golden falcon', 'the', dining_room)
falcon.treasure = True

### main ###

print "The Swallows"
print "============"
print

for chapter in range(1, 16):
    print "CHAPTER %d" % chapter
    print "-----------"
    print

    for paragraph in range(1, 33):
        events = []
        while len(events) < 20:
            alice.live()
            bob.live()
        for event in events:
          sys.stdout.write(str(event) + "  ")
          #sys.stdout.write("\n")
        print
        print
