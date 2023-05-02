#import pygtail

#tail = pygtail.Pygtail("retry.log", save_on_end=False, copytruncate=False)

#for line, offset in tail.with_offsets():
#    print(line)

# figure out right offset to save
#tail.write_offset_to_file(right_offset)

from pygtail import Pygtail

for line in Pygtail("retry.log"):
    print(line)
