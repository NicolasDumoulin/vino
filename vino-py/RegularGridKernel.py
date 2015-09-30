# -*- coding: utf8 -*-

import numpy as np
from Kernel import Kernel
from overrides import overrides

class RegularGridKernel(Kernel):
  def __init__(self, originCoords, dimensionsSteps, dimensionsExtents=None, data=None, metadata = {}):
    super(RegularGridKernel, self).__init__(metadata)
    self.originCoords = originCoords
    self.dimensionsSteps = dimensionsSteps
    self.dimensionsExtents = dimensionsExtents
    if data != None:
      self.setGrid(data)
    elif (dimensionsExtents != None):
      self.grid = np.zeros(dimensionsExtents, dtype='bool')
    
  @staticmethod   
  @overrides
  def getFormatCode():
    return "grid"
       
  @classmethod
  @overrides
  def initFromHDF5(cls, metadata, dataAttributes, data):
    '''
    Create an object of class BarGridKernel from attributes and data loaded from an HDF5 file. This method is intended to be used by the method hdf5common.readKernel
    '''
    return cls(dataAttributes['origin'], dataAttributes['steps'], data=data, metadata=metadata)
    
  @overrides
  def getData(self):
    return self.grid
    
  def setGrid(self, grid):
    self.dimensionsExtents = grid.shape
    self.grid = grid
    
  def set(self, coords, value):
    self.grid.put([coords], value)
      
  def get(self, coords):
    return self.grid[coords]
  
  @overrides
  def isInside(self, point):
    # TODO
    raise NotImplementedError

if __name__ == "__main__":
  from hdf5common import HDF5Manager
  grid = RegularGridKernel([0,0,0], [1,1,1], [10,10,10])
  grid.set([3,1,0], True)
  HDF5Manager.writeKernel(grid, 'test.h5')