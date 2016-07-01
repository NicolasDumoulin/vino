from BarGridKernel import BarGridKernel
from hdf5common import HDF5Manager,HDF5Writer,HDF5Reader
import re
import METADATA
import time

def CompareProcedure():
    with HDF5Reader('2Dlake_light.h5') as f:
      # TODO nothing is done with these metadata
      metadata = f.readMetadata()
      # reading the data attributes for determining the format
      dataAttributes = f.readDataAttributes()
      data = f.readData()
    print dataAttributes['intervals']
    print dataAttributes[METADATA.resultformat_name]
     
    bargridoh = BarGridKernel.initFromHDF5(metadata, dataAttributes, data)

    hm = HDF5Manager([BarGridKernel])
    bargrid = hm.readKernel('2Dlake_light.h5')

    bargrid2 = BarGridKernel.readPatrickSaintPierrebis('../samples/2D_light.txt')

    distancegriddimensions = [31,31] #[301,301]
    distancegridintervals = map(lambda e: e-1, distancegriddimensions)

    resizebargrid = bargrid.toBarGridKernel(bargrid.originCoords, bargrid.oppositeCoords, distancegridintervals)
    resizebargrid2 = bargrid2.toBarGridKernel(bargrid2.originCoords, bargrid2.oppositeCoords, distancegridintervals)

    print(bargrid.bars[0])
    print(bargrid2.bars[0])
    print(bargrid.bars[10000])
    print(bargrid2.bars[10000])
    for i in range(len(bargrid.bars)):
        if bargrid.bars[i][2]!=bargrid2.bars[i][2]:
            print bargrid.bars[i]
            print bargrid2.bars[i]

    print(bargrid.originCoords)
    print(bargridoh.originCoords)
    print(bargrid.oppositeCoords)
    print(bargridoh.oppositeCoords)
    print(bargrid.intervalNumberperaxis)
    print(bargridoh.intervalNumberperaxis)
    print(bargrid.permutation)
    print(bargridoh.permutation)


    print(resizebargrid.bars[0])
    print(resizebargrid2.bars[0])
    print(resizebargrid.bars[30])
    print(resizebargrid2.bars[30])
    for i in range(len(resizebargrid.bars)):
        if resizebargrid.bars[i][2]!=resizebargrid2.bars[i][2]:
            print resizebargrid.bars[i]
            print resizebargrid2.bars[i]
            print "merde"
    print "youpi"


def testRead():
    hm = HDF5Manager([BarGridKernel])
    
    grid = BarGridKernel.readPatrickSaintPierrebis('../samples/2D.txt')
    myre = re.compile('^#(.*):(.*)$')
    with open('../samples/2D_metadata.txt') as f:
      for line in f:
        if line.startswith('#'):
          k,v = myre.match(line).groups()
          grid.metadata[k.strip()]=v.strip()
    grid.metadata['results.submissiondate'] = time.strftime('%Y-%m-%d %H:%M',time.localtime()) 
    print grid.permutation
    print grid.originCoords
    hm.writeKernel(grid, '2Dlake.h5')
    grid2 = hm.readKernel('2Dlake.h5')
#    print(grid2.metadata)
#    print(metadata.category)
    print(grid2.metadata[METADATA.category])
    print(grid2.metadata[METADATA.results_submissiondate])
    print(grid2.metadata[METADATA.results_formatparametervalues])
    print grid2.permutation
    print grid2.originCoords


def testReadEssai():
    hm = HDF5Manager([BarGridKernel])
    
    grid = BarGridKernel.readPatrickSaintPierrebis('../samples/2D_light.txt')
    myre = re.compile('^#(.*):(.*)$')
    with open('../samples/2D_platform.txt') as f:
      for line in f:
        if line.startswith('#'):
          k,v = myre.match(line).groups()
          grid.metadata[k.strip()]=v.strip()
    grid.metadata['results.submissiondate'] = time.strftime('%Y-%m-%d %H:%M',time.localtime()) 
    hm.writeKernel(grid, '2D_metadata_from_platform.h5')
    grid2 = hm.readKernel('2D_metadata_from_platform.h5')
#    print(grid2.metadata)
#    print(metadata.category)
    print(grid2.metadata[METADATA.category])
    print(grid2.metadata[METADATA.results_submissiondate])


if __name__ == "__main__":
    testRead()
#    CompareProcedure()