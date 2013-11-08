#!/usr/bin/env python

#
# Example of extending _The Swallows_ world to produce a different story.
#

from os.path import realpath, dirname, join
import sys

# get the ../src/ directory onto the Python module search path
sys.path.insert(0, join(dirname(realpath(sys.argv[0])), '..', 'src'))

# now we can:
from swallows.engine.events import LegacyPublisher
from swallows.engine.objects import Male

# the following is not good.  but it works.
# better options would be:
# - define the world-specific behaviour of the characters in swallows.world
# - (less better) have alice & bob take these objects as dependency injections
import swallows.engine.objects
import swallows.story.world
swallows.engine.objects.revolver = swallows.story.world.revolver
swallows.engine.objects.brandy = swallows.story.world.brandy
swallows.engine.objects.dead_body = swallows.story.world.dead_body

# we extend it by adding a new character
fred = Male('Fred')

### main ###

publisher = LegacyPublisher(
    characters=(
        swallows.story.world.alice,
        swallows.story.world.bob,
        fred
    ),
    setting=swallows.story.world.house,
    title="My _The Swallows_ Fanfic",
    #debug=True,
)
publisher.publish()
