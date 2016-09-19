from context import infinity
import time
from infinity import InfinityBase

base = InfinityBase()
base.connect()

# these tag ids will be different to yours...
LUKE         = [0, 4, 125, 103, 226, 124, 67, 128]
IRON_MAN     = [0, 4, 131, 130, 242, 59, 53, 128]
RAPUNZEL     = [0, 4, 130, 247, 2, 147, 47, 128]
SPIDERMAN    = [0, 4, 60, 154, 234, 58, 53, 128]
JACK_SPARROW = [0, 4, 66, 176, 106, 125, 47, 128]
MERIDA       = [0, 4, 166, 54, 122, 150, 51, 128]

YELLOW = [255, 92, 0]
GLOW = [10, 10, 10]
RED = [255, 0, 0]
LIGHT_BLUE = [40, 40, 255]
PINK = [255, 40, 40]
PURPLE = [220, 30, 30]
OFF = [0, 0, 0]

def setColors(base_to_tag):
    for b in [1,2,3]:
        if b in base_to_tag:
            people = base_to_tag[b]
            if SPIDERMAN in people:
                base.setColor(b, *RED)
            elif IRON_MAN in people:
                base.setColor(b, *YELLOW)
            elif RAPUNZEL in people:
                base.setColor(b, *PINK)
            elif LUKE in people:
                base.setColor(b, *LIGHT_BLUE)
            elif JACK_SPARROW in people:
                base.setColor(b, *PURPLE)
            else:
                base.setColor(b, *GLOW)
        else:
            base.setColor(b, *OFF)

def updateColors():
    base.getAllTags(setColors)

base.onTagsChanged = updateColors

updateColors()

while True:
    pass


