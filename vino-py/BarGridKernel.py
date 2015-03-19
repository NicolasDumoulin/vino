# -*- coding: utf8 -*-

import numpy as np
import h5py
from hdf5common import HDF5Writer

class BarGridKernel:
  def __init__(self, originCoords, dimensionsSteps):
    self.originCoords = originCoords
    self.dimensionsSteps = dimensionsSteps
    self.bars = []
    
  def addBar(self, coords, inf, sup):
    self.bars.append(coords[:] + [inf,sup])
      
  def getBars(self):
    return self.bars
  
  def writeHDF5(self, filename):
    with HDF5Writer(filename) as w:
      w.writeMetadata([["name","foo"]], [["name","greatAlgo"]])
      w.writeData(np.array(self.bars,dtype='int16'), {
        'origin' : self.originCoords,
        'steps' : self.dimensionsSteps,
        'format' : 'bars'
          })
  
  def readHDF5(filename):
    with h5py.File(filename, 'r') as f:
      pass
    # TODO
  
if __name__ == "__main__":
  grid = BarGridKernel([0,0,0], [1,1,1])
  grid.addBar([1,2],3,4)
  grid.addBar([2,2],2,4)
  grid.addBar([2,3],3,4)
  grid.writeHDF5('test.h5')
  