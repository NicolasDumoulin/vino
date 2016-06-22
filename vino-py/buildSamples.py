from BarGridKernel import BarGridKernel
from hdf5common import HDF5Manager
import re
import METADATA

def testRead():
    hm = HDF5Manager([BarGridKernel])
    grid = BarGridKernel.readPatrickSaintPierrebis('../samples/2D.txt')
    myre = re.compile('^#(.*):(.*)$')
    with open('../samples/2D_metadata.txt') as f:
      for line in f:
        if line.startswith('#'):
          k,v = myre.match(line).groups()
          grid.metadata[k.strip()]=v.strip()
    hm.writeKernel(grid, 'test.h5')
    grid2 = hm.readKernel('test.h5')
#    print(grid2.metadata)
#    print(metadata.category)
    print(grid2.metadata[METADATA.category])

if __name__ == "__main__":
    testRead()