#!/usr/bin/env python

#
# Example of extending _The Swallows_ world to produce a different story.
#

from os.path import realpath, dirname, join
import sys

# get the ../src/ directory onto the Python module search path
sys.path.insert(0, join(dirname(realpath(sys.argv[0])), '..', 'src'))

# now we can:
from swallows.engine.events import Publisher
from swallows.story.characters import MaleCharacter
from swallows.story.world import (
    alice, bob, house, upstairs_hall,
    revolver, brandy, dead_body
)
from swallows.engine.objects import (
    ProperContainer, Item, Location
)

# we extend the world of The Swallows by adding a new character.
# note that we have to inform the new character of certain important objects
# in the world are, so that he can react sensibly to them.
# (you *can* pass other objects here, for example 'revolver=brandy', in which
# case the character will act fairly nonsensibly, threatening other characters
# with the bottle of brandy and so forth)
fred = MaleCharacter('Fred',
    revolver=revolver,
    brandy=brandy,
    dead_body=dead_body,
)

# we extend the world by adding new locations and objects
# note that locations exited-to and from must be imported from swallows.story.world (above)
# "Location" is imported from swallows.engine.objects
freds_office = Location("Fred's office")
freds_office.set_exits(upstairs_hall)

upstairs_hall.set_exits(freds_office) # adds to existing (unknown) exits

# we extend the world by adding some Objects
# "ProperContainer" and "Item" are imported from swallows.engine.objects
desk = ProperContainer("Fred's desk", location=freds_office)
pencils = Item('box of pencils', location=desk)


### main ###

publisher = Publisher(
    characters=(
        alice,
        bob,
        fred,
    ),
    setting=house,
    title="My _The Swallows_ Fanfic",
    #debug=True,
)
publisher.publish()
