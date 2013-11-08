#!/usr/bin/env python

#
# the_swallows.py: a novel generator.
# Chris Pressey, Cat's Eye Technologies
#

from os.path import realpath, dirname, join
import sys

# get the ../src/ directory onto the Python module search path
sys.path.insert(0, join(dirname(realpath(sys.argv[0])), '..', 'src'))

# now we can import things, like:
from swallows.engine.events import LegacyPublisher

# the following is not good.  but it works.
# better options would be:
# - define the world-specific behaviour of the characters in swallows.world
# - (less better) have alice & bob take these objects as dependency injections
import swallows.engine.objects
import swallows.story.world
swallows.engine.objects.revolver = swallows.story.world.revolver
swallows.engine.objects.brandy = swallows.story.world.brandy
swallows.engine.objects.dead_body = swallows.story.world.dead_body

### main ###

publisher = LegacyPublisher(
    characters=(
        swallows.story.world.alice,
        swallows.story.world.bob,
    ),
    setting=swallows.story.world.house,
    title="Title TBD (Book Four of _The Swallows_ series)",
    #debug=True,
)
publisher.publish()
