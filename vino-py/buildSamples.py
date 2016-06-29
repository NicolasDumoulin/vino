from BarGridKernel import BarGridKernel
from hdf5common import HDF5Manager,HDF5Writer
import re
import METADATA
import time


def testRead():
    hm = HDF5Manager([BarGridKernel])
    
    grid = BarGridKernel.readPatrickSaintPierrebis('../samples/2D_light.txt')
    myre = re.compile('^#(.*):(.*)$')
    with open('../samples/2D_light_metadata.txt') as f:
      for line in f:
        if line.startswith('#'):
          k,v = myre.match(line).groups()
          grid.metadata[k.strip()]=v.strip()
    grid.metadata['results.submissiondate'] = time.strftime('%Y-%m-%d %H:%M',time.localtime()) 
    hm.writeKernel(grid, '2Dlake_light.h5')
    grid2 = hm.readKernel('2Dlake_light.h5')
#    print(grid2.metadata)
#    print(metadata.category)
    print(grid2.metadata[METADATA.category])
    print(grid2.metadata[METADATA.results_submissiondate])


if __name__ == "__main__":
    testRead()