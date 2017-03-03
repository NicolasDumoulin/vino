from BarGridKernel import BarGridKernel
from KdTree import KdTree
from hdf5common import HDF5Manager,HDF5Writer,HDF5Reader
import re
import METADATA
import time
import FileFormatLoader

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
    bargrid2 = FileFormatLoader.PspModifiedLoader().read('../samples/2D_light.txt')

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
            print "merde"

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
    dataway = '../samples/2D.txt'
    metadataway = '../samples/2D_metadata.txt'
    h5way = '2D.h5'
    hm = HDF5Manager([BarGridKernel])
    
    grid = FileFormatLoader.PspModifiedLoader().read(dataway)
    myre = re.compile('^#(.*):(.*)$')
    with open(metadataway) as f:
      for line in f:
        if line.startswith('#'):
          k,v = myre.match(line).groups()
          grid.metadata[k.strip()]=v.strip()
    grid.metadata[METADATA.statedimension] = int(grid.metadata[METADATA.statedimension])
    grid.metadata['results.submissiondate'] = time.strftime('%Y-%m-%d %H:%M',time.localtime()) 
    print grid.permutation
    print grid.originCoords
    hm.writeKernel(grid, h5way)
    grid = []
#    grid2 = hm.readKernel(h5way)
#    print(grid2.metadata)
#    print(metadata.category)
#    print(grid2.metadata[METADATA.category])
#    print(grid2.metadata[METADATA.results_submissiondate])
#    print(grid2.metadata[METADATA.results_formatparametervalues])
#    print grid2.permutation
#    print grid2.originCoords
#    print(grid2.kernelMinPoint)
#    print(grid2.kernelMaxPoint)
    return grid

def testReadKdTree(): 
    dataway = '../samples/3D_languesIsa_dil0.txt'
    metadataway = '../samples/3D_languesIsa_dil0_metadata.txt'
    h5way = '3D_languesIsa_dil0.h5'
    hm = HDF5Manager([KdTree])
    metadata = {}
    myre = re.compile('^#(.*):(.*)$')
    with open(metadataway) as f:
        for line in f:
            if line.startswith('#'):
                k, v = myre.match(line).groups()
                metadata[k.strip()] = v.strip()
    metadata[METADATA.statedimension] = int(metadata[METADATA.statedimension])
    metadata['results.submissiondate'] = time.strftime('%Y-%m-%d %H:%M',time.localtime()) 
#    return metadata
    
    explorationdomain = metadata[METADATA.results_softwareparametervalues].split("/")[0].split(",")
    origin = explorationdomain[:len(explorationdomain)/2]
    opposite = explorationdomain[len(explorationdomain)/2:]    
    k = KdTree.readViabilitree(dataway, metadata,origin,opposite)
    print(k.cells[0])
    print("Kdtree loaded with %d cells" % len(k.cells))
    hm.writeKernel(k, h5way)
    k2 = hm.readKernel(h5way)
    return k2
    

    
if __name__ == "__main__":
    g=testRead()
#    CompareProcedure()
#    k=testReadKdTree()