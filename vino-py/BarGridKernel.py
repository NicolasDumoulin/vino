# -*- coding: utf8 -*-

import numpy as np
import re
from overrides import overrides
from sortedcontainers import SortedList
from Kernel import Kernel
from RegularGridKernel import RegularGridKernel

class BarGridKernel(Kernel):
  def __init__(self, originCoords, dimensionsSteps, data = [], metadata = {}):
    super(BarGridKernel, self).__init__(metadata)
    self.originCoords = originCoords
    self.dimensionsSteps = dimensionsSteps
    self.bars = SortedList(data)
    
  @staticmethod   
  @overrides
  def getFormatCode():
    return "bars"
       
  @classmethod
  @overrides
  def initFromHDF5(cls, metadata, dataAttributes, data):
    '''
    Create an object of class BarGridKernel from attributes and data loaded from an HDF5 file. This method is intended to be used by the method hdf5common.readKernel
    '''
    return cls(dataAttributes['origin'], dataAttributes['steps'], data.tolist(), metadata)
    
  @overrides
  def getData(self):
    return np.array(self.bars.as_list(),dtype='int64')
    
  def toRegularGridKernel(self):
    '''
    Convert the kernel to the regular grid representation.
    Returns an instance of RegularGridKernel.
    The returned grid is trimed to not include empty portion of grid.
    '''
    minPoint = np.array(self.kernelMinPoint)
    maxPoint = np.array(self.kernelMaxPoint)
    dimensionsExtents = maxPoint - minPoint + 1
    grid = RegularGridKernel(self.originCoords, self.dimensionsSteps,
                             dimensionsExtents, metadata=self.metadata)
    for bar in self.bars:
      barPosition = (bar[:-2]-minPoint[:-1]).tolist()
      grid.grid[tuple(barPosition)].put(range(bar[-2],bar[-1]+1),True)
    return grid                             
    
  def resample(self, newOrigin, newDimensionsSteps):
    '''
    Resample the discrete grid on a new one, supposed to be more coarse.
    '''
    # TODO
    raise NotImplementedError
    
  def addBar(self, coords, inf, sup):
    self.bars.add(coords[:] + [inf,sup])
    self.kernelMinPoint[:-1] = [min(x) for x in zip(self.kernelMinPoint[:-1],coords)]
    self.kernelMinPoint[-1] = min(self.kernelMinPoint[-1], inf)
    self.kernelMaxPoint[:-1] = [max(x) for x in zip(self.kernelMaxPoint[:-1],coords)]
    self.kernelMaxPoint[-1] = max(self.kernelMaxPoint[-1], sup)

      
  def getBars(self):
    return self.bars
  
  def getHDF5(self):
    return 

  @classmethod
  def readPatrickSaintPierre(cls, filename):
    '''
    Returns an object of class BarGridKernel loaded from an output file from the software of Patric Saint-Pierre.
    '''
    modelMetadata=[]
    bgk = None
    with open(filename, 'r') as f:
      f.readline()
      nbDim = re.match('\s*([0-9]*)\s.*',f.readline()).group(1)
      modelMetadata.append(['dynamic', f.readline()])
      modelMetadata.append(['constraints', f.readline()])
      modelMetadata.append(['target', f.readline()])
      for i in range(4): f.readline()
      dimensionsSteps = map(int, re.findall('[0-9]+', f.readline()))
      for i in range(2): f.readline()
      origin = map(int, re.findall('[0-9]+', f.readline()))
      maxPoint = map(int, re.findall('[0-9]+', f.readline()))
      for i in range(5): f.readline()
      bgk = cls(origin, dimensionsSteps)
      # reading until some lines with 'Initxx'
      stop=False
      initxx=False
      bgk.kernelMinPoint = origin
      bgk.kernelMaxPoint = maxPoint
      while not stop:
        line = f.readline()
        if 'Initxx' in line:
          initxx = True
        elif initxx and 'Initxx' not in line:
          stop=True
      # reading bars
      for line in f:
        coords = map(int, re.findall('[0-9]+', line))
        bgk.addBar(coords[:-2], coords[-2], coords[-1])
      # TODO what is done with modelMetadata and nbDim
    return bgk
  
  @overrides
  def isInside(self, point):
    raise NotImplementedError

if __name__ == "__main__":
  #grid = BarGridKernel([0,0,0], [1,1,1])
  #grid.addBar([1,2],3,4)
  #grid.addBar([2,2],2,4)
  #grid.addBar([2,3],3,4)
  #grid.writeHDF5('test.h5')
  
  import time
  import timeit
  startTime = time.time()
  grid = BarGridKernel.readPatrickSaintPierre('../samples/4D_005_light2.txt')
  readTime = time.time() - startTime
  print('reading raw txt in {:.2f}s'.format(readTime))
  from hdf5common import HDF5Manager
  hm = HDF5Manager([BarGridKernel])
  startTime = time.time()
  regularGrid = grid.toRegularGridKernel()
  print('conversion in {:.2f}s'.format(time.time() - startTime))
  for setup,data in [
#    ['from __main__ import grid, hm',[
#      ['converting to a regular grid', 'print(grid.toRegularGridKernel().grid.shape)']
#      ]],
    ['from __main__ import grid, hm',[
      ['writing hdf5', "hm.writeKernel(grid, 'test.h5')"],
      ['writing hdf5/gzip',"hm.writeKernel(grid, 'test_gzip9.h5', compression='gzip', compression_opts=9)"],
      ['writing hdf5/lzf',"hm.writeKernel(grid, 'test_lzf.h5', compression='lzf')"],
      ]],
    ['from __main__ import hm',[
      ['reading hdf5', "hm.readKernel('test.h5')"],
      ['reading hdf5/lzf', "hm.readKernel('test_lzf.h5')"],
      ['reading hdf5/gzip',"hm.readKernel('test_gzip9.h5')"]
      ]]
    ]:
      for message,command in data:
        print('{} in {:.2f}s'.format(message, timeit.timeit(command,setup=setup,number=20)/20))

  
 