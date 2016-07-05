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
    def __init__(self, cells=[], metadata={}):
        super(KdTree, self).__init__(metadata)
        self.cells = cells

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
        dim = self.getStateDimension()
        return [dim + x * 2 for x in range(dim)]
    
    def getMaxBoundsCoordinates(self):
        dim = self.getStateDimension()
        return [dim + x * 2 + 1 for x in range(dim)]
    
    @staticmethod   
    @overrides
    def getFormatCode():
        return "kdtree"

    @classmethod  
    def readViabilitreeFile(cls, f, metadata):
        cells = []
        dim = metadata[METADATA.statedimension]
        f.readline()
        for line in f:
            row = line.split()
            cells.append(map(float, row[:3 * dim]))        
        return cls(cells, metadata)
    
    @classmethod  
    def readViabilitree(cls, filename, metadata):
        '''
        Returns a kernel loaded from an output file from the software viabilitree.
        '''
        with open(filename, 'r') as f:
            return cls.readViabilitreeFile(f, metadata)

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
  
    def toBarGridKernel(self, intervalsSizes, newOriginCoords = None, newOppositeCoords = None):
        '''
        Convert to a BarGridKernel with another underlying grid, with a given size of intervals per axis.
        If no origin or opposite is given, it will be deduced from the lower or upper cell.
        Returns an instance of BarGridKernel.
        '''
        minBoundsCoordinates = self.getMinBoundsCoordinates()
        intervalsSizes = np.array(intervalsSizes, float)
        if not newOriginCoords:
            newOriginCoords = np.array([min([c[i] for c in self.cells]) for i in minBoundsCoordinates], float) + intervalsSizes / 2
        else:
            newOriginCoords = np.array(newOriginCoords, float)
        if not newOppositeCoords:
            newOppositeCoords = np.array([max([c[i+1] for c in self.cells]) for i in minBoundsCoordinates], float) - intervalsSizes / 2
        else:
            newOppositeCoords = np.array(newOppositeCoords, float)
        newIntervalNumberperaxis = (newOppositeCoords - newOriginCoords) / intervalsSizes
        bgk = BarGridKernel(newOriginCoords, newOppositeCoords, newIntervalNumberperaxis)
        for cell in self.cells:
            cell_start = [cell[i] for i in minBoundsCoordinates]
            cell_end = [cell[i+1] for i in minBoundsCoordinates]
            start_int = np.floor(newIntervalNumberperaxis * (np.array(cell_start, float) + intervalsSizes / 2 - newOriginCoords)/(newOppositeCoords - newOriginCoords))
            end_int = np.ceil(newIntervalNumberperaxis * (np.array(cell_end, float) - intervalsSizes / 2 - newOriginCoords)/(newOppositeCoords - newOriginCoords))
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
    import re
    metadata = {}
    myre = re.compile('^#(.*):(.*)$')
    with open('../samples/lake/lake_Isa_R1.txt') as f:
        for line in f:
            if line.startswith('#'):
                k, v = myre.match(line).groups()
                metadata[k.strip()] = v.strip()
    metadata[METADATA.statedimension] = int(metadata[METADATA.statedimension])
    k = KdTree.readViabilitree("../samples/lake/lake_Isa_R1_dat.txt", metadata)
    print(k.cells[0])
    print("Kdtree loaded with %d cells" % len(k.cells))
    print([1]*k.getStateDimension())
    bgk = k.toBarGridKernel([0.0001]*k.getStateDimension())
    print("KdTree converted to BarGrid with %d bars" % len(bgk.bars))