#!/usr/bin/env python

from swallows.objects import (
    Location, ProperLocation, Treasure, PluralTreasure,
    Container, ProperContainer,
    Item, Weapon, Horror, Male, Female
)
from swallows.util import pick

# TODO

# World:
# more reacting to the dead body:
# - if they *agree*, take one of the courses of action
# - if they *disagree*, well... the revolver may prove persuasive
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
bobs_bedroom = ProperLocation("Bob's bedroom")
alices_bedroom = ProperLocation("Alice's bedroom")

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

bobs_bed = ProperContainer("Bob's bed", location=bobs_bedroom)
alices_bed = ProperContainer("Alice's bed", location=alices_bedroom)

brandy = Item('bottle of brandy', location=liquor_cabinet)
revolver = Weapon('revolver', location=pick([bobs_bed, alices_bed]))
dead_body = Horror('dead body', location=bathroom)

alice = Female('Alice')
bob = Male('Bob')

ALL_ITEMS = (falcon, jewels, revolver, brandy)
