#!/usr/bin/env python

#
# Example of using _The Swallows_ engine, but not its world,
# to produce a different story.
#

from os.path import realpath, dirname, join
import sys

# get the ../src/ directory onto the Python module search path
sys.path.insert(0, join(dirname(realpath(sys.argv[0])), '..', 'src'))

# now we can:
from swallows.engine.events import Publisher
from swallows.engine.objects import Location, ProperLocation, Male, Female

### world ###

main_street = ProperLocation("Main Street")
butchers = Location("butcher's")
bakery = Location("bakery")
candlestick_factory = Location("candlestick factory")

main_street.set_exits(butchers, bakery, candlestick_factory)
butchers.set_exits(main_street)
bakery.set_exits(main_street)
candlestick_factory.set_exits(main_street)

downtown = (main_street, butchers, bakery, candlestick_factory)

class Tweedle(Male):
    def live(self):
        self.wander()

tweedledee = Tweedle('Tweedledee')
tweedledum = Tweedle('Tweedledum')

### main ###

publisher = Publisher(
    characters=(
        tweedledee,
        tweedledum,
    ),
    setting=downtown,
    title="TERRIBLE EXAMPLE STORY",
    #debug=True,
)
publisher.publish()
