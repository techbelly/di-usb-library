Disney Infinity USB Base library 
================================

Python. Requires hidapi.

Tested with the PS3/4 and Wii U base. I think the XBox bases are different and so likely won't work.

```python

from infinity import InfinityBase

base = InfinityBase()

# this will be run whenever a figure or disk is added/removed
base.onTagsChanged = lambda: print("Tags added or removed.")

base.connect()

# get all the figures and disks on the base 
base.getAllTags(print)

base.setColor(1, 200, 0, 0)

base.setColor(2, 0, 56, 0)

base.fadeColor(3, 0, 0, 200)

time.sleep(3)

base.flashColor(3, 0, 0, 200)

while True:
    pass
    
```
