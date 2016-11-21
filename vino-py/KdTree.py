from hdf5common import HDF5Reader, HDF5Manager
from BarGridKernel import BarGridKernel
from Kernel import Kernel
import METADATA
import numpy as np
from overrides import overrides
from sortedcontainers import SortedListWithKey

class KdTree(Kernel):
    '''
    KdTree store for each cell the coordinate of the sample point in the cell,
    and then for each dimension the min and the max of the cell.
    '''
    def __init__(self, cells=[], metadata={},origin=None,opposite=None):
        super(KdTree, self).__init__(metadata)
        self.cells = cells
        if origin:
            self.originCoords = np.array(origin,float)
        else:
            self.originCoords = self.getMinBounds()
        if opposite:
            self.oppositeCoords = np.array(opposite,float)
        else:
            self.oppositeCoords = self.getMaxBounds()


    @property
    def cells(self):
        '''
        Considering N the number of dimension of the system, each cell contains:
          - N coordinates for the sampled point
          - N couples of coordinates for the lower and higher point of the parallelotope
        '''
        return self.__cells

    @cells.setter
    def cells(self, cells):
        # sort cells by ascendant order of lower boundaries
        maxCoordinatesIndex = self.getMaxBoundsCoordinates()
        self.__cells = SortedListWithKey(cells, key=lambda cell: [cell[i] for i in maxCoordinatesIndex])
    
    def getMinBoundsCoordinates(self):
        '''
        Returns the indexes for retrieving the min bounds in the array of data of a tree node.
        '''
        dim = self.getStateDimension()
        return [dim + x * 2 for x in range(dim)]
    
    def getMaxBoundsCoordinates(self):
        '''
        Returns the indexes for retrieving the max bounds in the array of data of a tree node.
        '''
        dim = self.getStateDimension()
        return [dim + x * 2 + 1 for x in range(dim)]

    def getMinBounds(self):
        return np.array([min([c[i] for c in self.cells]) for i in self.getMinBoundsCoordinates()], float)

    def getMaxBounds(self):
        return np.array([max([c[i] for c in self.cells]) for i in self.getMaxBoundsCoordinates()], float)

    def getMinFrameworkBounds(self):
        return list(self.originCoords)

    def getMaxFrameworkBounds(self):
        return list(self.oppositeCoords)
    
    @staticmethod   
    @overrides
    def getFormatCode():
        return "kdtree"

    @overrides
    def getDataAttributes(self):
        da = super(KdTree, self).getDataAttributes()
        da['origin'] = self.originCoords
        da['opposite'] = self.oppositeCoords
        return da         

    def getDataToPlot(self):
        data = []
        data = [self.getMinFrameworkBounds()+self.getMaxFrameworkBounds()]+list(self.cells)
        return data

    @classmethod
    @overrides
    def initFromHDF5(cls, metadata, attrs, data):
        '''
      Create an object of class KdTree from attributes and data loaded from an HDF5 file. This method is intended to be used by the method hdf5common.readKernel
      '''
        return cls(cells=data.tolist(), metadata=metadata,origin=attrs['origin'], opposite=attrs['opposite'], )

    @overrides
    def getData(self):
        return np.array(list(self.cells), dtype='float')


    @classmethod  
    def readViabilitreeFile(cls, f, metadata,origin=None,opposite=None):
        cells = []
        dim = metadata[METADATA.statedimension]
        f.readline()
        for line in f:
            row = line.split()
            cells.append(map(float, row[:3 * dim]))        
        return cls(cells, metadata,origin,opposite)
    
    @classmethod  
    def readViabilitree(cls, filename, metadata,origin=None,opposite=None):
        '''
        Returns a kernel loaded from an output file from the software viabilitree.
        '''
        with open(filename, 'r') as f:
            return cls.readViabilitreeFile(f, metadata,origin,opposite)

    @overrides
    def isInSet(self, point):
        '''
        Returns if point belongs to the BarGridKernel.
        '''
        # creating a cell like in the kd-tree. Only lower bounds items will be considered for bisect
        cell = [0] * self.getStateDimension() + [e for e in point for i in range(2)]
        cellBeforeIndex = max(0, self.cells.bisect_left(cell)-1)
        cellBefore = self.cells[cellBeforeIndex]
        minCoords = self.getMinBoundsCoordinates()
        maxCoords = self.getMaxBoundsCoordinates()
        if all([point[i] >= cellBefore[minCoords[i]] and point[i] <= cellBefore[minCoords[i] + 1] for i in range(self.getStateDimension())]):
            return True
        while cellBeforeIndex + 1 < len(self.cells) and  point[0]<=self.cells[cellBeforeIndex + 1][maxCoords[0]]:
            cellBeforeIndex += 1
            cellBefore = self.cells[cellBeforeIndex]
            if all([point[i] >= cellBefore[minCoords[i]] and point[i] <= cellBefore[minCoords[i] + 1] for i in range(self.getStateDimension())]):
                return True
        return False
  
    @overrides
    def toBarGridKernel(self, newOriginCoords, newOppositeCoords, intervalNumberperaxis):
        '''
        Convert to a BarGridKernel with another underlying grid, with a given number of intervals per axis.
        If no origin or opposite is given, it will be deduced from the lower or upper cell.
        Returns an instance of BarGridKernel.
        '''
        minBoundsCoordinates = self.getMinBoundsCoordinates()
        intervalsSizes = (np.array([max([c[i+1] for c in self.cells]) for i in minBoundsCoordinates], float)-np.array([min([c[i] for c in self.cells]) for i in minBoundsCoordinates], float))/(np.array(intervalNumberperaxis)+np.array([1]*len(intervalNumberperaxis)))
        if not newOriginCoords:
            newOriginCoords = np.array([min([c[i] for c in self.cells]) for i in minBoundsCoordinates], float) + intervalsSizes / 2
        else:
            newOriginCoords = np.array(newOriginCoords, float)
        if not newOppositeCoords:
            newOppositeCoords = np.array([max([c[i+1] for c in self.cells]) for i in minBoundsCoordinates], float) - intervalsSizes / 2
        else:
            newOppositeCoords = np.array(newOppositeCoords, float)
#        newIntervalNumberperaxis = (newOppositeCoords - newOriginCoords) / intervalsSizes
        bgk = BarGridKernel(newOriginCoords, newOppositeCoords, intervalNumberperaxis)
#        print list(newOppositeCoords)
#        print list(intervalsSizes)

        for cell in self.cells:
            cell_start = [cell[i] for i in minBoundsCoordinates]
            cell_end = [cell[i+1] for i in minBoundsCoordinates]
            start_int = np.floor(np.array(intervalNumberperaxis) * (np.array(cell_start, float) + intervalsSizes / 2 - newOriginCoords)/(newOppositeCoords - newOriginCoords))
            start_int = np.array([max(start_int[i],0) for i in range(len(start_int))],int)

            end_int = np.ceil(np.array(intervalNumberperaxis) * (np.array(cell_end, float) - intervalsSizes / 2 - newOriginCoords)/(newOppositeCoords - newOriginCoords))
            end_int = np.array([min(end_int[i],intervalNumberperaxis[i]) for i in range(len(end_int))],int)
            # now adding all the points on the grid of the BGK between start and end of the Kd cell
            next_point = list(start_int[:-1])
            bgk.addBar(next_point, start_int[-1], end_int[-1])
            while any(next_point!=end_int[:-1]):
                for i,coord in reversed(list(enumerate(next_point))):
                    if next_point[i] < end_int[i]:
                        next_point[i] += 1
                        break
                    else:
                        next_point[i] = start_int[i]
                bgk.addBar(next_point, start_int[-1], end_int[-1])
        return bgk


if __name__ == "__main__":
    data = []
    minbounds = []
    maxbounds = []
    neworigin = []
    newopposite = []

    resizebargrids = []
    hm = HDF5Manager([BarGridKernel])
    bargrid = hm.readKernel('2Dlake_light.h5')
    data1 = bargrid.getDataToPlot()

    intervalSizes = np.array(bargrid.getIntervalSizes())
    if (len(minbounds) > 0):
        minbounds = [min(minbounds[i],list(np.array(bargrid.getMinBounds())-intervalSizes/2)[i]) for i in range(len(minbounds))]
        maxbounds = [max(maxbounds[i],list(np.array(bargrid.getMaxBounds())+intervalSizes/2)[i]) for i in range(len(maxbounds))]

    else :
        minbounds = list(np.array(bargrid.getMinBounds())-intervalSizes/2)
	maxbounds = list(np.array(bargrid.getMaxBounds())+intervalSizes/2)
    '''
    #To delete to show the original bargrid
    distancegriddimensions = [10,10]#[int(ppa),int(ppa)] #[301,301]
    distancegridintervals = map(lambda e: e-1, distancegriddimensions)
    bargridbis = bargrid.toBarGridKernel(bargrid.originCoords, bargrid.oppositeCoords, distancegridintervals)
    data.append(bargridbis.getDataToPlot())
    '''  
    distancegriddimensions = [10,10]
    newintervalsizes = (np.array(maxbounds)-np.array(minbounds))/np.array(distancegriddimensions)
    neworigin = list(np.array(minbounds)+newintervalsizes/2)
    newopposite = list(np.array(maxbounds)-newintervalsizes/2)
    distancegridintervals = map(lambda e: e-1, distancegriddimensions)
    resizebargrids.append(bargrid.toBarGridKernel(neworigin, newopposite, distancegridintervals))
    data.append(resizebargrids[-1].getDataToPlot())
    data2=resizebargrids[-1].getDataToPlot()

    hm = HDF5Manager([KdTree])
    kdt = hm.readKernel('2D_lake_Isa.h5')
#    data.append(kdt.getDataToPlot())
    
'''
if __name__ == "__main__":
    import re
    metadata = {}
    myre = re.compile('^#(.*):(.*)$')
    with open('../samples/lake/2D_lake_Isa_metadata.txt') as f:
        for line in f:
            if line.startswith('#'):
                k, v = myre.match(line).groups()
                metadata[k.strip()] = v.strip()
    metadata[METADATA.statedimension] = int(metadata[METADATA.statedimension])
    k = KdTree.readViabilitree("../samples/lake/lake_Isa_R1_dat.txt", metadata)
    print(k.cells[0])
    print("Kdtree loaded with %d cells" % len(k.cells))
    print([1]*k.getStateDimension())
    bgk = k.toBarGridKernelbis([50]*k.getStateDimension())
    print("KdTree converted to BarGrid with %d bars" % len(bgk.bars))
    data = k.getDataToPlot()
'''