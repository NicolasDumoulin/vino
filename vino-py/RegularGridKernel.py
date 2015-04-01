# -*- coding: utf8 -*-

import numpy as np
import h5py
from hdf5common import HDF5Writer

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
  
  def writeHDF5(self, filename, **datasets_options):
    with HDF5Writer(filename) as w:
      w.writeMetadata([["name","foo"]], [["name","greatAlgo"]])
      w.writeData(self.grid, {
        'origin' : self.originCoords,
        'steps' : self.dimensionsSteps,
        'format' : 'grid'
          }, **datasets_options)
 
  def writeHDF5_coords(self, filename, **datasets_options):
    with HDF5Writer(filename) as w:
      w.writeMetadata([["name","foo"]], [["name","greatAlgo"]])
      coords_list = [[i,j] for i,row in enumerate(self.grid) for j,e in enumerate(row) if e]
      print(float(len(coords_list))/self.grid.size)
      w.writeData(coords_list, {
        'origin' : self.originCoords,
        'steps' : self.dimensionsSteps,
        'format' : 'grid'
          }, **datasets_options)
 
  def readHDF5(filename):
    with h5py.File(filename, 'r') as f:
      pass
    # TODO
  
if __name__ == "__main__":
  grid = RegularGridKernel([0,0,0], [1,1,1], [10,10,10])
  grid.set([3,1,0], True)
  grid.writeHDF5('test.h5')