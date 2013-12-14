# Copyright (c)2013 Chris Pressey, Cat's Eye Technologies
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import random

from swallows.engine.objects import (
    Location, ProperLocation, Treasure, PluralTreasure,
    Container, ProperContainer,
    Item, Weapon, Horror
)
from swallows.story.characters import MaleCharacter, FemaleCharacter

# TODO

# World:
# more reacting to the dead body:
# - if they *agree*, take one of the courses of action
# after agreement:
# - calling the police (do they have a landline?  it might be entertaining
#   if they share one mobile phone between the both of them)
#   - i'll have to introduce a new character... the detective.  yow.
# - trying to dispose of it... they try to drag it to... the garden?
#   i'll have to add a garden.  and a shovel.
# an unspeakable thing in the basement!  (don't they have enough excitement
#   in their lives?)
# bullets for the revolver

### world ###

alice = FemaleCharacter('Alice')
bob = MaleCharacter('Bob')

kitchen = Location('kitchen')
living_room = Location('living room')
dining_room = Location('dining room')
front_hall = Location('front hall')
driveway = Location('driveway', noun="driveway")
garage = Location('garage', noun="garage")
path_by_the_shed = Location('path by the shed', noun="path")
shed = Location('shed', noun="shed")
upstairs_hall = Location('upstairs hall')
study = Location('study')
bathroom = Location('bathroom')
bobs_bedroom = ProperLocation("<*> bedroom", owner=bob)
alices_bedroom = ProperLocation("<*> bedroom", owner=alice)

kitchen.set_exits(dining_room, front_hall)
living_room.set_exits(dining_room, front_hall)
dining_room.set_exits(living_room, kitchen)
front_hall.set_exits(kitchen, living_room, driveway, upstairs_hall)
driveway.set_exits(front_hall, garage, path_by_the_shed)
garage.set_exits(driveway)
path_by_the_shed.set_exits(driveway, shed)
shed.set_exits(path_by_the_shed)
upstairs_hall.set_exits(bobs_bedroom, alices_bedroom, front_hall, study, bathroom)
bobs_bedroom.set_exits(upstairs_hall)
alices_bedroom.set_exits(upstairs_hall)
study.set_exits(upstairs_hall)
bathroom.set_exits(upstairs_hall)

house = (kitchen, living_room, dining_room, front_hall, driveway, garage,
         upstairs_hall, bobs_bedroom, alices_bedroom, study, bathroom,
         path_by_the_shed, shed)

falcon = Treasure('golden falcon', location=dining_room)
jewels = PluralTreasure('stolen jewels', location=garage)

cupboards = Container('cupboards', location=kitchen)
liquor_cabinet = Container('liquor cabinet', location=dining_room)
mailbox = Container('mailbox', location=driveway)

bobs_bed = ProperContainer("<*> bed", location=bobs_bedroom, owner=bob)
alices_bed = ProperContainer("<*> bed", location=alices_bedroom, owner=alice)

brandy = Item('bottle of brandy', location=liquor_cabinet)
revolver = Weapon('revolver', location=random.choice([bobs_bed, alices_bed]))
dead_body = Horror('dead body', location=bathroom)

# when making alice and bob, we let them recognize certain important
# objects in their world
for c in (alice, bob):
    c.configure_objects(
        revolver=revolver,
        brandy=brandy,
        dead_body=dead_body,
    )

ALL_ITEMS = (falcon, jewels, revolver, brandy)
