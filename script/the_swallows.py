#!/usr/bin/env python

#
# the_swallows.py: a novel generator.
# Chris Pressey, Cat's Eye Technologies
#

from os.path import realpath, dirname, join
import sys

# get the ../src/ directory onto the Python module search path
sys.path.insert(0, join(dirname(realpath(sys.argv[0])), '..', 'src'))

# now we can:
from swallows.world import alice, bob, house
from swallows.util import pick
from swallows.events import EventCollector, Editor

# this is not good.  but it works.
# better options would be:
# - define the world-specific behaviour of the characters in swallows.world
# - (less better) have alice & bob take these objects as dependency injections
import swallows.objects
import swallows.world
swallows.objects.revolver = swallows.world.revolver
swallows.objects.brandy = swallows.world.brandy
swallows.objects.dead_body = swallows.world.dead_body

### main ###

FRIFFERY = False
DEBUG = False

print "Title TBD (Book Four of _The Swallows_ series)"
print "=============================================="
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

        actor_order = (alice, bob)
        # this leads to continuity problems:
        #if random.randint(0, 1) == 0:
        #    actor_order = (bob, alice)
        while len(pov_actor.collector.events) < 20:
            for actor in actor_order:
                actor.live()

        if FRIFFERY:
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

        if DEBUG:
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

        if not DEBUG:
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
