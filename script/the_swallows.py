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
from swallows.events import LegacyPublisher

# the following is not good.  but it works.
# better options would be:
# - define the world-specific behaviour of the characters in swallows.world
# - (less better) have alice & bob take these objects as dependency injections
import swallows.objects
import swallows.world
swallows.objects.revolver = swallows.world.revolver
swallows.objects.brandy = swallows.world.brandy
swallows.objects.dead_body = swallows.world.dead_body

### main ###

publisher = LegacyPublisher(
    characters=(
        swallows.world.alice,
        swallows.world.bob,
    ),
    setting=swallows.world.house,
    title="Title TBD (Book Four of _The Swallows_ series)",
    #debug=True,
)
publisher.publish()
