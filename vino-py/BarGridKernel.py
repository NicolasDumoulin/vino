# -*- coding: utf8 -*-

import numpy as np
import re
from overrides import overrides
from sortedcontainers import SortedList
from Kernel import Kernel
from RegularGridKernel import RegularGridKernel

class BarGridKernel(Kernel):
  def __init__(self, originCoords, oppositeCoords, intervalNumberperaxis, permutation = None, data = [], metadata = {}):
    super(BarGridKernel, self).__init__(metadata)
    self.originCoords = np.array(originCoords,float)
    self.oppositeCoords = np.array(oppositeCoords,float)
    self.intervalNumberperaxis = np.array(intervalNumberperaxis,float)
    self.bars = SortedList(data)
    if permutation is None :
        self.permutation = np.eye(len(originCoords))
    else :
        self.permutation = permutation
    self.kernelMaxPoint  = [-1]*len(originCoords)
    self.kernelMinPoint = []
    for i in range(len(originCoords)):
        self.kernelMinPoint.append(1)

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
    return np.array(list(self.bars),dtype='int64')
    
  def getTotalPointNumber(self):
      return sum(map(lambda elt: elt[-1] - elt[-2], self.bars))
    
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

   
  def intersectionwithBarGridKernel(self,othergrid):
    '''
    Returns an instance of BarGridKernel which is the intersection of two BarGridKernels
    with the same underlying grid characteristics 
    '''
    data = []
    grid = BarGridKernel(self.originCoords,self.oppositeCoords,self.intervalNumberperaxis,self.permutation,data,self.metadata)
    barsindex = 0
    otherbarsindex = 0
    while (barsindex < len(self.bars)) and (otherbarsindex < len(othergrid.bars)):
        actualbarposition = self.bars[barsindex][:-2]
        print "actualbarposition[0] ::%d " %actualbarposition[0]
  
        while (otherbarsindex < len(othergrid.bars)) and (othergrid.bars[otherbarsindex][:-2] < self.bars[barsindex][:-2]):
            otherbarsindex = otherbarsindex + 1
#        if (othergrid.bars[otherbarsindex][:-2] == self.bars[barsindex][:-2]):
        while (barsindex < len(self.bars)) and (otherbarsindex < len(othergrid.bars)) and (othergrid.bars[otherbarsindex][:-2] == self.bars[barsindex][:-2]):
            if othergrid.bars[otherbarsindex][-1] < self.bars[barsindex][-2]:
                otherbarsindex = otherbarsindex + 1
            elif othergrid.bars[otherbarsindex][-2] > self.bars[barsindex][-1]:
                barsindex = barsindex + 1
            elif othergrid.bars[otherbarsindex][-1] > self.bars[barsindex][-1]:
                grid.addBar(self.bars[barsindex][:-2], max(othergrid.bars[otherbarsindex][-2], self.bars[barsindex][-2]), self.bars[barsindex][-1])
                barsindex = barsindex + 1
            elif othergrid.bars[otherbarsindex][-1] < self.bars[barsindex][-1]:
                grid.addBar(self.bars[barsindex][:-2], max(othergrid.bars[otherbarsindex][-2], self.bars[barsindex][-2]), othergrid.bars[otherbarsindex][-1])
                otherbarsindex = otherbarsindex + 1
            else:
                grid.addBar(self.bars[barsindex][:-2], max(othergrid.bars[otherbarsindex][-2], self.bars[barsindex][-2]), othergrid.bars[otherbarsindex][-1])
                otherbarsindex = otherbarsindex + 1
                barsindex = barsindex + 1
                       
        while (barsindex < len(self.bars)) and (othergrid.bars[otherbarsindex][:-2] > self.bars[barsindex][:-2]):
            barsindex = barsindex + 1
    return grid                             

  def MinusBarGridKernel(self,othergrid):
    '''
    Returns an instance of BarGridKernel which is the element of the BarGridKernels
    which are not in the other one. The Bargridkernel have the same underlying grid characteristics 
    '''
    data = []
    grid = BarGridKernel(self.originCoords,self.oppositeCoords,self.intervalNumberperaxis,self.permutation,data,self.metadata)
    barsindex = 0
    otherbarsindex = 0
    while (barsindex < len(self.bars)) and (otherbarsindex < len(othergrid.bars)):
#        actualbarposition = self.bars[barsindex][:-2]
#        print "actualbarposition[0] ::%d " %actualbarposition[0]
  
        while (otherbarsindex < len(othergrid.bars)) and (othergrid.bars[otherbarsindex][:-2] < self.bars[barsindex][:-2]):
            otherbarsindex = otherbarsindex + 1
        alreadycut = False
        while (barsindex < len(self.bars)) and (otherbarsindex < len(othergrid.bars)) and (othergrid.bars[otherbarsindex][:-2] == self.bars[barsindex][:-2]):
            if othergrid.bars[otherbarsindex][-1] < self.bars[barsindex][-2]:
                otherbarsindex = otherbarsindex + 1
            elif othergrid.bars[otherbarsindex][-1] >= self.bars[barsindex][-1]:
                if othergrid.bars[otherbarsindex][-2] > self.bars[barsindex][-2]:                
                    if alreadycut:
                        grid.addBar(self.bars[barsindex][:-2], remember, othergrid.bars[otherbarsindex][-2]-1)
                    else :
                        grid.addBar(self.bars[barsindex][:-2], self.bars[barsindex][-2], othergrid.bars[otherbarsindex][-2]-1)
                barsindex = barsindex + 1
                alreadycut = False
            else :
                if othergrid.bars[otherbarsindex][-2] > self.bars[barsindex][-2]:
                    if alreadycut:
                        grid.addBar(self.bars[barsindex][:-2], remember, othergrid.bars[otherbarsindex][-2]-1)
                    else :
                        grid.addBar(self.bars[barsindex][:-2], self.bars[barsindex][-2], othergrid.bars[otherbarsindex][-2]-1)
                otherbarsindex = otherbarsindex + 1
                alreadycut = True
                remember = othergrid.bars[otherbarsindex][-1]+1
                  
        while (barsindex < len(self.bars)) and (othergrid.bars[otherbarsindex][:-2] > self.bars[barsindex][:-2]):
                if alreadycut:
                    grid.addBar(self.bars[barsindex][:-2], remember, self.bars[barsindex][-1])
                    barsindex = barsindex + 1
                    alreadycut = False
                else :
                    grid.addBar(self.bars[barsindex][:-2], self.bars[barsindex][-2], self.bars[barsindex][-1])
                    barsindex = barsindex + 1
    return grid                             

    
  def toBarGridKernel(self, newOriginCoords, newOppositeCoords, newIntervalNumberperaxis):
    '''
    Convert a BarGridKernel to another BarGridKernel with another underlying grid.
    Returns an instance of BarGridKernel.
    '''
    dimension = len(self.originCoords)
    actualbarposition = np.zeros(dimension-1,int)
    barsindex = 0
    # converting to numpy arrays
    newOriginCoords = np.array(newOriginCoords,float)
    newIntervalNumberperaxis = np.array(newIntervalNumberperaxis,float)
    permutnewOriginCoords = np.dot(self.permutation, newOriginCoords)
    # permuting coordinates
    permutnewIntervalNumberperaxis = np.dot(self.permutation, newIntervalNumberperaxis)
    permutnewpas = np.dot(self.permutation,(np.array(newOppositeCoords,float) - newOriginCoords) / newIntervalNumberperaxis)
    permutOriginCoords = np.dot(self.permutation, self.originCoords)
    permutinversepas = np.dot(self.permutation, (newIntervalNumberperaxis / self.oppositeCoords - self.originCoords))
    data = []
    grid = BarGridKernel(newOriginCoords,newOppositeCoords,newIntervalNumberperaxis,self.permutation,data,self.metadata)

    while(actualbarposition[0]<permutnewIntervalNumberperaxis[0]+1):
        realpoint = permutnewOriginCoords[:-1] + actualbarposition * permutnewpas[:-1]
        intpoint = (realpoint-permutOriginCoords[:-1]) * permutinversepas[:-1]
        intpoint = map(lambda e: int(e+0.5), intpoint)    
        while (barsindex < len(self.bars)) and (self.bars[barsindex][:2] < intpoint):
            barsindex = barsindex+1
        barinprocess = False
        while (barsindex < len(self.bars)) and (self.bars[barsindex][:-2] == intpoint):
            inf = self.bars[barsindex][-2]
            realinf = inf/permutinversepas[-1] +permutOriginCoords[-1]
            intinf = int((realinf-permutnewOriginCoords[-1])/permutnewpas[-1]+0.5)
            sup = self.bars[barsindex][-1]
            realsup = sup/permutinversepas[-1] +permutOriginCoords[-1]
            intsup = int((realsup-permutnewOriginCoords[-1])/permutnewpas[-1]+0.5)
            if (intinf<permutnewIntervalNumberperaxis[-1]+1) or (intsup >=0):
                if barinprocess == True :
                    if intinf == grid.bars[-1][-1]:
                        grid.bars[-1][-1] = min(intsup,permutnewIntervalNumberperaxis[-1]+1)
                    else :
                        grid.addBar(actualbarposition.tolist(), max(intinf,0), min(intsup,permutnewIntervalNumberperaxis[-1]+1))
                else :
                    grid.addBar(actualbarposition.tolist(), max(intinf,0), min(intsup,permutnewIntervalNumberperaxis[-1]+1))
                    barinprocess = True
            barsindex = barsindex+1
        for i in range(dimension-1):
            if (actualbarposition[dimension-2-i]<permutnewIntervalNumberperaxis[dimension-2-i]+1):
                actualbarposition[dimension-2-i] = actualbarposition[dimension-2-i]+1
                break
    return grid                             


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
      # ND Why? Why not opposite = maxPoint
      opposite = origin      
      bgk = cls(origin, opposite, dimensionsSteps)
      # reading until some lines with 'Initxx'
      stop=False
      initxx=False
      # ND Why restrict min/max point to integer position
      bgk.kernelMinPoint = map(lambda e: e//1, origin)
      bgk.kernelMaxPoint = map(lambda e: e//1, maxPoint)
      while not stop:
        line = f.readline()
        if 'Initxx' in line:
          initxx = True
        elif initxx and 'Initxx' not in line:
          stop=True
      # reading bars
      for line in f:
        coords = map(int, re.findall('[0-9]+', line))
        # ND Why convert point to integer position
        coords = map(lambda e: e//1, coords)
        bgk.addBar(coords[2:-2], coords[-2], coords[-1])
      # TODO what is done with modelMetadata and nbDim
    return bgk
  
  @classmethod  
  def readPatrickSaintPierreFile(cls, f):
    '''
    Returns an object of class BarGridKernel loaded from an output file from the software of Patrick Saint-Pierre.
    '''
    bgk = None
    origin = map(int, re.findall('[0-9]+', f.readline()))
    dimension = len(origin)
    opposite = map(int, re.findall('[0-9]+', f.readline()))
    intervalNumber = map(int, re.findall('[0-9]+', f.readline()))

    pointSize = map(int, re.findall('[0-9]+', f.readline()))
    intervalNumber = map(lambda e: e//pointSize[0], intervalNumber)
    # reading columns headers and deducing permutation of variables
    line = f.readline()
    columnNumbertoIgnore = len(re.findall('empty', line))
    permutVector = map(int, re.findall('[0-9]+', line))
    permutation = np.zeros(dimension * dimension,int).reshape(dimension,dimension)
    for i in range(dimension):
        permutation[i][permutVector[i]-1]=1
    # Ok, creating the container object
    bgk = cls(origin, opposite, intervalNumber,permutation)
    # ignoring lines until 'Initxx'
    stop=False
    while not stop:
      line = f.readline()
      if 'Initxx' in line:
        stop=True
    # reading bars
    stop = False
    while not stop:
      # using a while loop, because the for loop seems buggy with django InMemoryUploadedFile reading
      line = f.readline()
      if not line:
        stop=True
      else:
        coords = map(int, re.findall('[0-9]+', line))
        coords = map(lambda e: e//pointSize[0], coords)
        bgk.addBar(coords[columnNumbertoIgnore:-2], coords[-2], coords[-1])
        # TODO what is done with modelMetadata and nbDim
    return bgk

  @classmethod  
  def readPatrickSaintPierrebis(cls, filename):
    '''
    Returns an object of class BarGridKernel loaded from an output file from the software of Patric Saint-Pierre.
    '''
    with open(filename, 'r') as f:
      return cls.readPatrickSaintPierreFile(f)      
  
  @overrides
  def isInside(self, point_initial):
    '''
    Returns if point_initial belongs to the BarGridKernel
    '''
    b = False
    origin = self.originCoords
    point_init = np.array(point_initial,float)
    opposite = self.oppositeCoords
    intervalnumber = self.intervalNumberperaxis
    point_int = intervalnumber * (point_init - origin)/(opposite - origin)
    point_int = map(lambda e: int(e+0.5), point_int)    

    point = np.dot(np.array(self.permutation),np.transpose(np.array(point_int))).tolist()
    l = len(point)      

    for bar in self.bars:
        i = 0        
        bb = True
        while i < (l-1):
            if point[i]!=bar[i]:
                bb = False                
                i = l-1
            else :
                i = i+1

        if bb :
            if (point[l-1]>=bar[l-1]) and (point[l-1]<=bar[l]):
                    b = True
                    break
    return b

if __name__ == "__main__":
  #grid = BarGridKernel([0,0,0], [1,1,1])
  #grid.addBar([1,2],3,4)
  #grid.addBar([2,2],2,4)
  #grid.addBar([2,3],3,4)
  #grid.writeHDF5('test.h5')
  
  import time
  import timeit
  import sys
  startTime = time.time()
  grid = BarGridKernel.readPatrickSaintPierrebis('../samples/2D.txt')

  total = grid.getTotalPointNumber()  
  print "grid totalpoint ::%d " %total

  readTime = time.time() - startTime
  print('reading raw txt in {:.2f}s'.format(readTime))
  print "minPoint ::%d " %grid.kernelMinPoint[0]
  print "maxPoint ::%d " %grid.kernelMaxPoint[0]
  from hdf5common import HDF5Manager
  hm = HDF5Manager([BarGridKernel])
#  startTime = time.time()
#  regularGrid = grid.toRegularGridKernel()
#  readTime = time.time() - startTime
#  print('converting to grid in {:.2f}s'.format(readTime))

  
  startTime = time.time()
  newgrid = grid.toBarGridKernel(grid.originCoords,grid.oppositeCoords,grid.intervalNumberperaxis)
  readTime = time.time() - startTime
  print('converting to new bargrid in {:.2f}s'.format(readTime))
  total2 = newgrid.getTotalPointNumber()  
  print "grid totalpoint ::%d " %total2

  grid.bars[0][-1] = 63241
  total = grid.getTotalPointNumber()  
  print "grid totalpoint ::%d " %total

  startTime = time.time()
  intersectgrid = grid.intersectionwithBarGridKernel(newgrid)
  readTime = time.time() - startTime
  print('intersection in {:.2f}s'.format(readTime))
  total = intersectgrid.getTotalPointNumber()  
  print "grid totalpoint ::%d " %total

  startTime = time.time()
  minusgrid = grid.MinusBarGridKernel(newgrid)
  readTime = time.time() - startTime
  print('minus in {:.2f}s'.format(readTime))
  total = minusgrid.getTotalPointNumber()  
  print "grid totalpoint ::%d " %total

  point =[20536,1]
  startTime = time.time()
  b = grid.isInside(point)
  readTime = time.time() - startTime
  print('isinside in {:.2f}s'.format(readTime))
  if b:
      print "il est dedans"
  else :
      print "il est dehors"
#  for setup,data in [
#    ['from __main__ import grid, hm',[
#      ['converting to a regular grid', 'print(grid.toRegularGridKernel().grid.shape)']
#      ]],
#    ['from __main__ import grid, hm',[
#      ['writing hdf5', "hm.writeKernel(grid, 'test.h5')"],
#      ['writing hdf5/gzip',"hm.writeKernel(grid, 'test_gzip9.h5', compression='gzip', compression_opts=9)"],
#      ['writing hdf5/lzf',"hm.writeKernel(grid, 'test_lzf.h5', compression='lzf')"],
#      ]],
#    ['from __main__ import hm',[
#      ['reading hdf5', "hm.readKernel('test.h5')"],
#      ['reading hdf5/lzf', "hm.readKernel('test_lzf.h5')"],
#      ['reading hdf5/gzip',"hm.readKernel('test_gzip9.h5')"]
#      ]]
#    ]:
#      for message,command in data:
#        print('{} in {:.2f}s'.format(message, timeit.timeit(command,setup=setup,number=20)/20))

  
 