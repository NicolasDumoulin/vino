# -*- coding: utf8 -*-

import numpy as np
import h5py
from hdf5common import HDF5Writer
import re

class BarGridKernel:
  def __init__(self, originCoords, dimensionsSteps):
    self.originCoords = originCoords
    self.dimensionsSteps = dimensionsSteps
    self.bars = []
    
  def addBar(self, coords, inf, sup):
    self.bars.append(coords[:] + [inf,sup])
      
  def getBars(self):
    return self.bars
  
  def writeHDF5(self, filename, **datasets_options):
    with HDF5Writer(filename) as w:
      w.writeMetadata([["name","foo"]], [["name","greatAlgo"]])
      w.writeData(np.array(self.bars,dtype='int16'), {
        'origin' : self.originCoords,
        'steps' : self.dimensionsSteps,
        'format' : 'bars'
          }, **datasets_options)
  
  def readHDF5(filename):
    with h5py.File(filename, 'r') as f:
      pass
    # TODO
  
  @staticmethod
  def readPatrickSaintPierre(filename):
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
      bgk = BarGridKernel(origin, dimensionsSteps)
      # reading until some lines with 'Initxx'
      stop=False
      initxx=False
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
    return bgk
  
if __name__ == "__main__":
  grid = BarGridKernel([0,0,0], [1,1,1])
  grid.addBar([1,2],3,4)
  grid.addBar([2,2],2,4)
  grid.addBar([2,3],3,4)
  #grid.writeHDF5('test.h5')
  
  grid = BarGridKernel.readPatrickSaintPierre('../../exemples noyaux/4D_005.txt')
  grid.writeHDF5('test.h5')
  grid.writeHDF5('test_gzip9.h5', compression="gzip", compression_opts=9)
  grid.writeHDF5('test_lzf.h5', compression="lzf")
  