# -*- coding: utf8 -*-
import os
import numpy as np
import re, math
from overrides import overrides
from sortedcontainers import SortedList
from Kernel import Kernel
from RegularGridKernel import RegularGridKernel

class BarGridKernel(Kernel):
  '''
  Store a kernel of n dimensions as a list of bars in the space of dimension (n-1).
  A bar is given by its start and its end coordinates, and corresponds to the
  hull of the viable points in the last dimension for each coordinates in the space
  of dimension (n-1).
  The order of the dimensions may have been changed, and the last dimension of these data
  may not correspond to the last dimension of the viability problem.
  Therefore the attribute ``permutation`` give a matrix describing the permutation of the dimension.
  '''
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

  @overrides
  def getDataAttributes(self):
    da = super(BarGridKernel, self).getDataAttributes()
    da['origin'] = self.originCoords
    da['opposite'] = self.oppositeCoords
    da['intervals'] = self.intervalNumberperaxis
    return da  
       
  @classmethod
  @overrides
  def initFromHDF5(cls, metadata, attrs, data):
    '''
    Create an object of class BarGridKernel from attributes and data loaded from an HDF5 file. This method is intended to be used by the method hdf5common.readKernel
    '''
    return cls(originCoords=attrs['origin'], oppositeCoords=attrs['opposite'], intervalNumberperaxis=attrs['intervals'], data=data.tolist(), metadata=metadata)
    
  @overrides
  def getData(self):
    return np.array(list(self.bars),dtype='int64')
    
  def getTotalPointNumber(self):
      return sum(map(lambda elt: elt[-1] - elt[-2] + 1, self.bars))
    
  def toRegularGridKernel(self):
    '''
    Convert the kernel to the regular grid representation.
    Returns an instance of RegularGridKernel.
    The returned grid is trimed to not include empty portion of grid.
    '''
    minPoint = np.array(self.kernelMinPoint)
    maxPoint = np.array(self.kernelMaxPoint)
    dimensionsExtents = maxPoint - minPoint + 1
    grid = RegularGridKernel(self.originCoords, self.intervalNumberperaxis,
                             dimensionsExtents, metadata=self.metadata)
    for bar in self.bars:
      barPosition = (bar[:-2]-minPoint[:-1]).tolist()
      grid.grid[tuple(barPosition)].put(range(bar[-2],bar[-1]+1),True)
    return grid                             

  def getInside(self):
    '''
    Returns an instance of BarGridKernel which is the points inside the original BarGridKernel 
    Attention pas pris encore en compte permutation éventuelle
    '''
    data = []
    tabaroundbarsindices = []
    dimension = len(self.originCoords)-1
    nbBars = len(self.bars)
    insidegrid = BarGridKernel(self.originCoords,self.oppositeCoords,self.intervalNumberperaxis,self.permutation,data,self.metadata)
    barsindex = 0
    for i in range(2*dimension):
        tabaroundbarsindices.append(0)

    while (barsindex < len(self.bars)):
 #   while (barsindex < 50):
      if (self.bars[barsindex][-1] - self.bars[barsindex][-2])>2:
        actualbarposition = self.bars[barsindex][:-2]
        totalborder = False
        tabaroundpositions = []

        for i in range(dimension*2):
            tabaroundpositions.append(self.bars[barsindex][:-2])
            tabaroundpositions[-1][i/2] = tabaroundpositions[-1][i/2] + 2*(i%2)-1
            if (tabaroundpositions[-1][i/2] <0) or (tabaroundpositions[-1][i/2] > self.intervalNumberperaxis[i/2]):
                totalborder = True                
                break
            else:
                while (tabaroundbarsindices[i] < nbBars) and (self.bars[tabaroundbarsindices[i]][:-2] < tabaroundpositions[-1]):
                    tabaroundbarsindices[i] = tabaroundbarsindices[i] + 1
                if (self.bars[tabaroundbarsindices[i]][:-2] > tabaroundpositions[-1]):
                    totalborder = True                    
                    break
 

        if not totalborder:
#            print('barsindex : %d tabarounindices : %d - %d' %(barsindex,tabaroundbarsindices[0],tabaroundbarsindices[1]))
#            print self.bars[barsindex][-2]+1
            mini = self.bars[barsindex][-2]+1
            maxi = self.intervalNumberperaxis[-1]
        while not totalborder:
            partialborder = False
            i = 0
            while ((not partialborder) and (i < dimension +1)):
#                print "i = %d" %i
#                print tabaroundbarsindices[i]                
                while ((tabaroundbarsindices[i] < nbBars) and (self.bars[tabaroundbarsindices[i]][:-2] == tabaroundpositions[i]) and (self.bars[tabaroundbarsindices[i]][-1] < mini)):
                    tabaroundbarsindices[i] = tabaroundbarsindices[i] + 1
                                        
#                print tabaroundbarsindices[i]
#                print self.bars[tabaroundbarsindices[i]]
#                print "mini"
#                print mini
#                print "maxi"
#                print maxi
#                    b= a.read()
                if ((tabaroundbarsindices[i] == nbBars) or (self.bars[tabaroundbarsindices[i]][:-2] > tabaroundpositions[i])):
                    totalborder = True
                    partialborder = True
 #                   print "sortie 1"
                elif (self.bars[tabaroundbarsindices[i]][-2] > self.bars[barsindex][-1]-1):
                    barsindex = barsindex + 1
                    while (barsindex < len(self.bars)) and (self.bars[barsindex][:-2] == actualbarposition) and ((self.bars[barsindex][-1] - self.bars[barsindex][-2])<=2):
                        barsindex = barsindex + 1
                    if ((barsindex == len(self.bars)) or (self.bars[barsindex][:-2] > actualbarposition)):
                        totalborder = True
                        partialborder = True
                    else :
                        partialborder = True                        
                        mini = self.bars[barsindex][-2]+1
                        maxi = self.intervalNumberperaxis[-1]
#                    print "sortie 2"
                elif (self.bars[tabaroundbarsindices[i]][-2] > maxi):
                    mini = self.bars[tabaroundbarsindices[i]][-2]
                    maxi = self.bars[tabaroundbarsindices[i]][-1]
                    i =0
#                    print "sortie 3"
                else :
                    mini = max(self.bars[tabaroundbarsindices[i]][-2],mini)
                    maxi = min(self.bars[tabaroundbarsindices[i]][-1],maxi)
                    i =i+1
#                    print "sortie 4"
            if not partialborder:
                if (maxi < self.bars[barsindex][-1]-1) :
                    insidegrid.addBar(self.bars[barsindex][:-2], mini, maxi)
                    mini = maxi + 2
                    maxi = self.intervalNumberperaxis[-1]
#                    print "sortie totale 1"
                else :
                    insidegrid.addBar(self.bars[barsindex][:-2], mini, self.bars[barsindex][-1]-1)
                    barsindex = barsindex + 1
                    while (barsindex < len(self.bars)) and (self.bars[barsindex][:-2] == actualbarposition) and ((self.bars[barsindex][-1] - self.bars[barsindex][-2])<=2):
                        barsindex = barsindex + 1
                    if ((barsindex == len(self.bars)) or (self.bars[barsindex][:-2] > actualbarposition)):
                        totalborder = True
 #                       print "sortie totale 2"
                    else :
                        mini = self.bars[barsindex][-2]+1
                        maxi = self.intervalNumberperaxis[-1]
 #                       print "sortie totale 3"

        while (barsindex < len(self.bars)) and (self.bars[barsindex][:-2] == actualbarposition):
                    barsindex = barsindex + 1
      else:
        barsindex = barsindex + 1          
    return insidegrid


  def getBorder(self):
    '''
    Returns an instance of BarGridKernel which is the points inside the original BarGridKernel 
    Attention pas pris encore en compte permutation éventuelle
    '''
    data = []
    tabaroundbarsindices = []
    dimension = len(self.originCoords)-1
    nbBars = len(self.bars)
    bordergrid = BarGridKernel(self.originCoords,self.oppositeCoords,self.intervalNumberperaxis,self.permutation,data,self.metadata)
    barsindex = 0
    for i in range(2*dimension):
        tabaroundbarsindices.append(0)

    while (barsindex < len(self.bars)):
#    while (barsindex < 100):
      alreadycut = False
      if (self.bars[barsindex][-1] - self.bars[barsindex][-2])>2:
        actualbarposition = self.bars[barsindex][:-2]
        totalborder = False
        tabaroundpositions = []

        for i in range(dimension*2):
            tabaroundpositions.append(self.bars[barsindex][:-2])
            tabaroundpositions[-1][i/2] = tabaroundpositions[-1][i/2] + 2*(i%2)-1
            if (tabaroundpositions[-1][i/2] <0) or (tabaroundpositions[-1][i/2] > self.intervalNumberperaxis[i/2]):
                totalborder = True                
                break
            else:
                while (tabaroundbarsindices[i] < nbBars) and (self.bars[tabaroundbarsindices[i]][:-2] < tabaroundpositions[-1]):
                    tabaroundbarsindices[i] = tabaroundbarsindices[i] + 1
                if (self.bars[tabaroundbarsindices[i]][:-2] > tabaroundpositions[-1]):
                    totalborder = True                    
                    break
 

        if totalborder:
            bordergrid.addBar(self.bars[barsindex][:-2], self.bars[barsindex][-2], self.bars[barsindex][-1])
            barsindex = barsindex + 1          
        else :
 #           print('barsindex : %d tabarounindices : %d - %d' %(barsindex,tabaroundbarsindices[0],tabaroundbarsindices[1]))
 #           print self.bars[barsindex][-2]+1
            mini = self.bars[barsindex][-2]+1
            maxi = self.intervalNumberperaxis[-1]
        while not totalborder:
            partialborder = False
            i = 0
            while ((not partialborder) and (i < dimension +1)):
  #              print "i = %d" %i
  #              print tabaroundbarsindices[i]                
                while ((tabaroundbarsindices[i] < nbBars) and (self.bars[tabaroundbarsindices[i]][:-2] == tabaroundpositions[i]) and (self.bars[tabaroundbarsindices[i]][-1] < mini)):
                    tabaroundbarsindices[i] = tabaroundbarsindices[i] + 1
                                        
#                print tabaroundbarsindices[i]
#                print self.bars[tabaroundbarsindices[i]]
#                print "mini"
#                print mini
#                print "maxi"
#                print maxi
#                  b= a.read()
                if ((tabaroundbarsindices[i] == nbBars) or (self.bars[tabaroundbarsindices[i]][:-2] > tabaroundpositions[i])):
                    totalborder = True
                    partialborder = True
                    if alreadycut :
                        bordergrid.addBar(self.bars[barsindex][:-2], remember, self.bars[barsindex][-1])
                        alreadycut = False
                    else : 
                        bordergrid.addBar(self.bars[barsindex][:-2], self.bars[barsindex][-2], self.bars[barsindex][-1])
                    barsindex = barsindex + 1          
 #                   print "sortie 1"
                elif (self.bars[tabaroundbarsindices[i]][-2] > self.bars[barsindex][-1]-1):
                    if alreadycut :
                        bordergrid.addBar(self.bars[barsindex][:-2], remember, self.bars[barsindex][-1])
                        alreadycut = False
                    else :
                        bordergrid.addBar(self.bars[barsindex][:-2], self.bars[barsindex][-2], self.bars[barsindex][-1])
                    barsindex = barsindex + 1
                    while (barsindex < len(self.bars)) and (self.bars[barsindex][:-2] == actualbarposition) and ((self.bars[barsindex][-1] - self.bars[barsindex][-2])<=2):
                        bordergrid.addBar(self.bars[barsindex][:-2], self.bars[barsindex][-2], self.bars[barsindex][-1])
                        barsindex = barsindex + 1
                    if ((barsindex == len(self.bars)) or (self.bars[barsindex][:-2] > actualbarposition)):
                        totalborder = True
                        partialborder = True
                    else :
                        partialborder = True                        
                        mini = self.bars[barsindex][-2]+1
                        maxi = self.intervalNumberperaxis[-1]
#                    print "sortie 2"
                elif (self.bars[tabaroundbarsindices[i]][-2] > maxi):
                    mini = self.bars[tabaroundbarsindices[i]][-2]
                    maxi = self.bars[tabaroundbarsindices[i]][-1]
                    i =0
#                    print "sortie 3"
                else :
                    mini = max(self.bars[tabaroundbarsindices[i]][-2],mini)
                    maxi = min(self.bars[tabaroundbarsindices[i]][-1],maxi)
                    i =i+1
#                    print "sortie 4"
            if not partialborder:
                if (maxi < self.bars[barsindex][-1]-1) :
                    if alreadycut :
                        bordergrid.addBar(self.bars[barsindex][:-2], remember,mini-1)
                    else :
                        bordergrid.addBar(self.bars[barsindex][:-2], self.bars[barsindex][-2],mini-1)
                        alreadycut = True
                    remember = maxi + 1
                    mini = maxi + 2
                    maxi = self.intervalNumberperaxis[-1]
#                    print "sortie totale 1"
                else :
                    if alreadycut :
                        bordergrid.addBar(self.bars[barsindex][:-2], remember, mini -1)
                    else : 
                        bordergrid.addBar(self.bars[barsindex][:-2], self.bars[barsindex][-2], mini -1)
                    alreadycut = False
                    bordergrid.addBar(self.bars[barsindex][:-2], self.bars[barsindex][-1], self.bars[barsindex][-1])
                    barsindex = barsindex + 1
                    while (barsindex < len(self.bars)) and (self.bars[barsindex][:-2] == actualbarposition) and ((self.bars[barsindex][-1] - self.bars[barsindex][-2])<=2):
                        bordergrid.addBar(self.bars[barsindex][:-2], self.bars[barsindex][-2], self.bars[barsindex][-1])
                        barsindex = barsindex + 1
                    if ((barsindex == len(self.bars)) or (self.bars[barsindex][:-2] > actualbarposition)):
                        totalborder = True
#                        print "sortie totale 2"
                    else :
                        mini = self.bars[barsindex][-2]+1
                        maxi = self.intervalNumberperaxis[-1]
#                        print "sortie totale 3"

        while (barsindex < len(self.bars)) and (self.bars[barsindex][:-2] == actualbarposition):
                    bordergrid.addBar(self.bars[barsindex][:-2], self.bars[barsindex][-2], self.bars[barsindex][-1])                    
                    barsindex = barsindex + 1
      else:
        bordergrid.addBar(self.bars[barsindex][:-2], self.bars[barsindex][-2], self.bars[barsindex][-1])
        barsindex = barsindex + 1          
    return bordergrid

   
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
                alreadycut = True
                remember = othergrid.bars[otherbarsindex][-1]+1
                otherbarsindex = otherbarsindex + 1
                  
        while (barsindex < len(self.bars)) and (otherbarsindex < len(othergrid.bars)) and (othergrid.bars[otherbarsindex][:-2] > self.bars[barsindex][:-2]):
                if alreadycut:
                    grid.addBar(self.bars[barsindex][:-2], remember, self.bars[barsindex][-1])
                    barsindex = barsindex + 1
                    alreadycut = False
                else :
                    grid.addBar(self.bars[barsindex][:-2], self.bars[barsindex][-2], self.bars[barsindex][-1])
                    barsindex = barsindex + 1
    if (otherbarsindex >= len(othergrid.bars)):
        while (barsindex < len(self.bars)):
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
    permutinversepas = np.dot(self.permutation, (self.intervalNumberperaxis / self.oppositeCoords - self.originCoords))
#    print permutinversepas
#    print permutnewpas
    data = []
    grid = BarGridKernel(newOriginCoords,newOppositeCoords,newIntervalNumberperaxis,self.permutation,data,self.metadata)

    while(actualbarposition[0]<permutnewIntervalNumberperaxis[0]+1):
#        print actualbarposition
        realpoint = permutnewOriginCoords[:-1] + actualbarposition * permutnewpas[:-1]
        intpoint = (realpoint-permutOriginCoords[:-1]) * permutinversepas[:-1]
        intpoint = map(lambda e: int(e+0.5), intpoint)
#        print intpoint
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
            if ((i == dimension - 2) or (actualbarposition[dimension-2-i]<permutnewIntervalNumberperaxis[dimension-2-i])):
                actualbarposition[dimension-2-i] = actualbarposition[dimension-2-i]+1
                break
            else :
                actualbarposition[dimension-2-i] = 0
                
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
    metadata=[]
    bgk = None
    with open(filename, 'r') as f:
      f.readline()
      nbDim = re.match('\s*([0-9]*)\s.*',f.readline()).group(1)
      metadata.append([MEDATADA.dynamicsdescription, f.readline()])
      metadata.append([MEDATADA.stateconstraintdescription, f.readline()])
      metadata.append([MEDATADA.targetdescription, f.readline()])
      for i in range(4): f.readline()
      dimensionsSteps = map(int, re.findall('[0-9]+', f.readline()))
      for i in range(2): f.readline()
      origin = map(int, re.findall('[0-9]+', f.readline()))
      maxPoint = map(int, re.findall('[0-9]+', f.readline()))
      for i in range(5): f.readline()
      # ND Why? Why not opposite = maxPoint
      opposite = origin      
      bgk = cls(origin, opposite, dimensionsSteps, metadata=metadata)
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
    
    #map(float, re.findall('-?\d+\.?\d*', 'rtyryry 0.3 ioyoyou 0.5555 lkjkjjml 6'))
    #origin = map(int, re.findall('[0-9]+', f.readline()))
    origin = map(float, re.findall('-?\d+\.?\d*', f.readline()))
    dimension = len(origin)
    opposite = map(float, re.findall('-?\d+\.?\d*', f.readline()))
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
  def isInSet(self, point):
    '''
    Returns if point belongs to the BarGridKernel.
    This method will find the cell where to lookup a bar containing the point. If not,
    the point is not considered in the set.
    Technical details:
    In a BarGrid, each cell of the (n-1) dimensional space is stored by its 
    index inside a matrix between two opposite points and the number of cells in each dimension.
    First, this method will compute the index(es) of the cell where to lookup for bars,
    then it will look for the last dimension to check if the point is inside a cell
    covered by a bar in the selected cell of the (n-1) dimensional space.
    Note that if the point is exactly between several cells (on a vertex or on an edge),
    the method will check the bars of all the touching cells.
    Let's consider s(i) the size of a cell (the step size) on the dimension i,
    p(i) the coordinates of the point requested on the dimension i, and
    c(i) the coordinates of the center of a cell of the BarGrid in the dimension i,
    thus we consider that the point p is inside the cell c if:
     - p(i)>=c(i)-s(i)/2 (after the left side of the cell)
     - p(i)<=c(i)+s(i)/2 (before the right side of the cell)
     - for i belongs to [0;n-1]
    '''
    result = False
    point = np.array(point,float)
    # first we need to project the point into the cells coordinate system
    point_int = self.intervalNumberperaxis * (point - self.originCoords)/(self.oppositeCoords - self.originCoords)
    points = [point_int]
    for i,coord in enumerate(point_int):
        new_points = []
        for p in points:
            if (coord%1)==0.5: # the point is exactly between two cells on the current dimension
                left = [pp for pp in p]
                left[i] = int(math.floor(left[i]))
                right = [pp for pp in p]
                right[i] = int(math.ceil(right[i]))
                new_points.extend([left, right])
            else:
                # we just need to round to the nearest cell center
                new_point = [pp for pp in p]
                new_point[i] = int(round(new_point[i]))
                new_points.append(new_point)
        points=new_points
    l = len(point)      
    # we will look at each bar if they are positioned in the coordinates
    # in (n-1) dimensions space than our point
    for point in points:
        candidateBar = False
        for bar in self.bars:
            if point[:-1]==bar[:-2]:
              # we have reached the interesting zone
              candidateBar = True
              # is our point in the bar?
              if (point[l-1]>=bar[l-1]-0.5) and (point[l-1]<=bar[l]+0.5):
                result = True
                break
            elif candidateBar:
              # we have passed the position in (n-1) dimensions space, so we can't find candidates anymore
              break
    return result

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
  grid = BarGridKernel.readPatrickSaintPierrebis('../samples/2D_light.txt')

  total = grid.getTotalPointNumber()  
  print "grid totalpoint ::%d " %total

  readTime = time.time() - startTime
  print('reading raw txt in {:.2f}s'.format(readTime))
  print "minPoint ::%d " %grid.kernelMinPoint[0]
  print "maxPoint ::%d " %grid.kernelMaxPoint[0]

  print grid.originCoords
  print grid.oppositeCoords
  print grid.intervalNumberperaxis
    
  distancegriddimensions = [1001,1001]
  distancegridintervals = map(lambda e: e-1, distancegriddimensions)
    
  resizebargrid = grid.toBarGridKernel(grid.originCoords, grid.oppositeCoords, distancegridintervals)
#  print resizebargrid.bars

  from hdf5common import HDF5Manager
  hm = HDF5Manager([BarGridKernel])
#  startTime = time.time()
#  regularGrid = grid.toRegularGridKernel()
#  readTime = time.time() - startTime
#  print('converting to grid in {:.2f}s'.format(readTime))

'''
  startTime = time.time()
  bordergrid = grid.getBorder()
  readTime = time.time() - startTime
  print('border in {:.2f}s'.format(readTime))
  total = bordergrid.getTotalPointNumber()  
  print "bordergrid totalpoint ::%d " %total
 
 
  
  
  startTime = time.time()
  insidegrid = grid.getInside()
  readTime = time.time() - startTime
  print('inside in {:.2f}s'.format(readTime))
  total = insidegrid.getTotalPointNumber()  
  print "insidegrid totalpoint ::%d " %total

  startTime = time.time()
  minusgrid = grid.MinusBarGridKernel(insidegrid)
  readTime = time.time() - startTime
  print('minus in {:.2f}s'.format(readTime))
  total = minusgrid.getTotalPointNumber()  
  print "grid totalpoint ::%d " %total
 
    
  
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
  b = grid.isInSet(point)
  readTime = time.time() - startTime
  print('isinside in {:.2f}s'.format(readTime))
  if b:
      print "il est dedans"
  else :
      print "il est dehors"
  '''

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

  
 