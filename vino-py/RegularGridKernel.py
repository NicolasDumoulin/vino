# -*- coding: utf8 -*-

import numpy as np
import h5py

class RegularGridKernel:
  def __init__(self, originCoords, dimensionsSteps, dimensionsExtents):
    self.originCoords = originCoords
    self.dimensionsSteps = dimensionsSteps
    self.dimensionsExtents = dimensionsExtents
    self.grid = np.full(dimensionsExtents, False, dtype='bool')
    
  def set(self, coords, value):
    self.grid[coords] = value
      
  def get(self, coords):
    return self.grid[coords]
  
  def writeHDF5(self, filename):
    with h5py.File(filename, 'w') as f:
      metadata = f.create_group('metadata')
      metadata['problem/model']=[["name","foo"]]
      metadata['algorithm']=[["name","greatAlgo"]]
      f['data'] = self.grid
      f['data'].attrs['origin']=self.originCoords
      f['data'].attrs['steps']=self.dimensionsSteps
      f['data'].attrs['format']="grid"
  
  def readHDF5(filename):
    with h5py.File(filename, 'r') as f:
      pass
    # TODO
  
if __name__ == "__main__":
  grid = RegularGridKernel([0,0,0], [1,1,1], [10,10,10])
  grid.set([3,1,0], True)
  grid.writeHDF5('test.h5')