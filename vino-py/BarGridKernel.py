# -*- coding: utf8 -*-

import numpy as np
import h5py
import hdf5common
from hdf5common import HDF5Writer, HDF5Reader
import re

class BarGridKernel:
  def __init__(self, originCoords, dimensionsSteps, data = []):
    self.originCoords = originCoords
    self.dimensionsSteps = dimensionsSteps
    self.bars = data
    
  @staticmethod
  def initFromHDF5(hdf5Attributes, data):
    '''
    Create an object of class BarGridKernel from attributes and data loaded from an HDF5 file. This method is intended to be used by the method hdf5common.readKernel
    '''
    return BarGridKernel(hdf5Attributes['origin'], hdf5Attributes['steps'], data)
    
  def addBar(self, coords, inf, sup):
    self.bars.append(coords[:] + [inf,sup])
      
  def getBars(self):
    return self.bars
  
  def writeHDF5(self, filename, **datasets_options):
    with HDF5Writer(filename) as w:
      w.writeMetadata([["name","foo"]], [["name","greatAlgo"]])
      w.writeData(np.array(self.bars,dtype='int64'), {
        'origin' : self.originCoords,
        'steps' : self.dimensionsSteps,
        'format' : 'bars'
          }, **datasets_options)   
  
  @staticmethod
  def readPatrickSaintPierre(filename):
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
  #grid = BarGridKernel([0,0,0], [1,1,1])
  #grid.addBar([1,2],3,4)
  #grid.addBar([2,2],2,4)
  #grid.addBar([2,3],3,4)
  #grid.writeHDF5('test.h5')
  
  import time
  import timeit
  startTime = time.time()
  grid = BarGridKernel.readPatrickSaintPierre('../samples/4D_005.txt')
  readTime = time.time() - startTime
  print('reading raw txt in {:.2f}s'.format(readTime))

  for setup,data in [
    ['from __main__ import grid',[
      ['writing hdf5', "grid.writeHDF5('test.h5')"],
      ['writing hdf5/gzip',"grid.writeHDF5('test_gzip9.h5', compression='gzip', compression_opts=9)"],
      ['writing hdf5/lzf',"grid.writeHDF5('test_lzf.h5', compression='lzf')"],
      ]],
    ['import hdf5common',[
      ['reading hdf5', "hdf5common.readKernel('test.h5')"],
      ['reading hdf5/lzf', "hdf5common.readKernel('test_lzf.h5')"],
      ['reading hdf5/gzip',"hdf5common.readKernel('test_gzip9.h5')"]
      ]]
    ]:
      for message,command in data:
        print('{} in {:.2f}s'.format(message, timeit.timeit(command,setup=setup,number=20)/20))

  
 