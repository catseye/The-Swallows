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
from swallows.engine.events import Publisher
from swallows.story.world import alice, bob, house

### main ###

publisher = Publisher(
    characters=(alice, bob),
    setting=house,
    title="Dial 'S' for Swallows (Unfinished Draft)",
    #debug=True,
    #chapters=1,
)
publisher.publish()
