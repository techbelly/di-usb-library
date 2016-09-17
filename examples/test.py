from context import infinity

from infinity import InfinityBase

import time

def futurePrint(s):
    print(s)

base = InfinityBase()

base.onTagsChanged = lambda: futurePrint("Tags added or removed.")

base.connect()

base.getAllTags(futurePrint)

base.setColor(1, 200, 0, 0)

base.setColor(2, 0, 56, 0)

base.fadeColor(3, 0, 0, 200)

time.sleep(3)

base.flashColor(3, 0, 0, 200)

print("Try adding and removing figures and discs to/from the base. CTRL-C to quit")
while True:
    pass

