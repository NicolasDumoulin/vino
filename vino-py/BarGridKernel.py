# -*- coding: utf8 -*-
import numpy as np
from overrides import overrides
from sortedcontainers import SortedList
import math
from Kernel import Kernel
from RegularGridKernel import RegularGridKernel
import copy

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
    def __init__(self, originCoords, oppositeCoords, intervalNumberperaxis, permutation=None, kernelMinPoint=None, kernelMaxPoint=None,data=[], metadata={}):
        super(BarGridKernel, self).__init__(metadata)
        self.originCoords = np.array(originCoords, float)
        self.oppositeCoords = np.array(oppositeCoords, float)
        self.intervalNumberperaxis = np.array(intervalNumberperaxis, int)
        self.bars = SortedList(data)
        if permutation is None:
            self.permutation = np.eye(len(originCoords),dtype = int)
        else:
            self.permutation = permutation
        if kernelMinPoint is None:
            self.kernelMinPoint = []
            for i in range(len(originCoords)):
                 self.kernelMinPoint.append(intervalNumberperaxis[i])
        else :
            self.kernelMinPoint = kernelMinPoint
        if kernelMaxPoint is None:
            self.kernelMaxPoint = [-1] * len(originCoords)
        else :
            self.kernelMaxPoint = kernelMaxPoint


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
        da['permutation']= self.permutation
        da['maxPoint']= self.kernelMaxPoint
        da['minPoint']= self.kernelMinPoint
        return da  
       
    @classmethod
    @overrides
    def initFromHDF5(cls, metadata, attrs, data):
        '''
      Create an object of class BarGridKernel from attributes and data loaded from an HDF5 file. This method is intended to be used by the method hdf5common.readKernel
      '''
        return cls(originCoords=attrs['origin'], oppositeCoords=attrs['opposite'], intervalNumberperaxis=attrs['intervals'],permutation=attrs['permutation'],kernelMinPoint=attrs['minPoint'],kernelMaxPoint=attrs['maxPoint'], data=data.tolist(), metadata=metadata)

    @overrides
    def getData(self):
        return np.array(list(self.bars), dtype='int64')


    def justepourtester(self,a,b):
        c = [a+a,b+b]
        return c

    def getIntervalSizes(self):
        '''
	Give the coordinates of the point of the grid with minimal coordinates
        ''' 
        intervalsizes = []
        intervalsizes = list((self.oppositeCoords-self.originCoords)/self.intervalNumberperaxis)
	return intervalsizes

    def getMinFrameworkBounds(self):
        return list(self.originCoords-np.array(self.getIntervalSizes())/2)

    def getMaxFrameworkBounds(self):
        return list(self.oppositeCoords+np.array(self.getIntervalSizes())/2)

    def getMinBounds(self):
        '''
	Give the coordinates of the point of the vino with minimal coordinates
        ''' 
        minbounds = []
        intervalSizes = np.array(self.getIntervalSizes())
        permutOriginCoords = np.dot(self.permutation, self.originCoords)
        permutOppositeCoords = np.dot(self.permutation, self.oppositeCoords)
        permutIntervalNumberperaxis = np.dot(self.permutation, self.intervalNumberperaxis)
        minbounds = list(np.dot(np.transpose(self.permutation),permutOriginCoords+(permutOppositeCoords-permutOriginCoords)*self.kernelMinPoint/permutIntervalNumberperaxis))
        minbounds = minbounds - intervalSizes/2
	return minbounds

    def getMaxBounds(self):
        '''
	Give the coordinates of the point of the vino with maximal coordinates
        ''' 
        maxbounds = []
        intervalSizes = np.array(self.getIntervalSizes())
        permutOriginCoords = np.dot(self.permutation, self.originCoords)
        permutOppositeCoords = np.dot(self.permutation, self.oppositeCoords)
        permutIntervalNumberperaxis = np.dot(self.permutation, self.intervalNumberperaxis)
        maxbounds = list(np.dot(np.transpose(self.permutation),permutOriginCoords+(permutOppositeCoords-permutOriginCoords)*self.kernelMaxPoint/permutIntervalNumberperaxis))
        maxbounds = maxbounds + intervalSizes/2
	return maxbounds

    def getDataToPlot(self):
        data = []

        permutOriginCoords = np.dot(self.permutation, self.originCoords)
        permutOppositeCoords = np.dot(self.permutation, self.oppositeCoords)
        permutIntervalNumberperaxis = np.dot(self.permutation, self.intervalNumberperaxis)
        for i in range(len(self.bars)):
           data.append(list(permutOriginCoords+(permutOppositeCoords-permutOriginCoords)*np.array(self.bars[i][:-1])/permutIntervalNumberperaxis)+[permutOriginCoords[-1]+(permutOppositeCoords[-1]-permutOriginCoords[-1])*self.bars[i][-1]/permutIntervalNumberperaxis[-1]])
        perm = np.dot(self.permutation,np.arange(len(self.originCoords)))
        data = [self.getMinFrameworkBounds()+self.getMaxFrameworkBounds()+self.getIntervalSizes()+list(perm)]+list(data)
        return data

    def getTotalPointNumber(self):
        return sum([elt[-1] - elt[-2] + 1 for elt in self.bars])

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
            grid.grid[tuple(barPosition)].put(list(range(bar[-2], bar[-1] + 1)), True)
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
                    mini = self.bars[barsindex][-2]+1
                    maxi = self.intervalNumberperaxis[-1]
                while not totalborder:
                    partialborder = False
                    i = 0
                    while ((not partialborder) and (i < dimension +1)):
                        while ((tabaroundbarsindices[i] < nbBars) and (self.bars[tabaroundbarsindices[i]][:-2] == tabaroundpositions[i]) and (self.bars[tabaroundbarsindices[i]][-1] < mini)):
                            tabaroundbarsindices[i] = tabaroundbarsindices[i] + 1
                        if ((tabaroundbarsindices[i] == nbBars) or (self.bars[tabaroundbarsindices[i]][:-2] > tabaroundpositions[i])):
                            totalborder = True
                            partialborder = True
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
                        elif (self.bars[tabaroundbarsindices[i]][-2] > maxi):
                            mini = self.bars[tabaroundbarsindices[i]][-2]
                            maxi = self.bars[tabaroundbarsindices[i]][-1]
                            i =0
                        else :
                            mini = max(self.bars[tabaroundbarsindices[i]][-2],mini)
                            maxi = min(self.bars[tabaroundbarsindices[i]][-1],maxi)
                            i =i+1
                    if not partialborder:
                        if (maxi < self.bars[barsindex][-1]-1) :
                            insidegrid.addBar(self.bars[barsindex][:-2], mini, maxi)
                            mini = maxi + 2
                            maxi = self.intervalNumberperaxis[-1]
                        else :
                            insidegrid.addBar(self.bars[barsindex][:-2], mini, self.bars[barsindex][-1]-1)
                            barsindex = barsindex + 1
                            while (barsindex < len(self.bars)) and (self.bars[barsindex][:-2] == actualbarposition) and ((self.bars[barsindex][-1] - self.bars[barsindex][-2])<=2):
                                barsindex = barsindex + 1
                            if ((barsindex == len(self.bars)) or (self.bars[barsindex][:-2] > actualbarposition)):
                                totalborder = True
                            else :
                                mini = self.bars[barsindex][-2]+1
                                maxi = self.intervalNumberperaxis[-1]
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
                    mini = self.bars[barsindex][-2]+1
                    maxi = self.intervalNumberperaxis[-1]
                while not totalborder:
                    partialborder = False
                    i = 0
                    while ((not partialborder) and (i < dimension +1)):
                        while ((tabaroundbarsindices[i] < nbBars) and (self.bars[tabaroundbarsindices[i]][:-2] == tabaroundpositions[i]) and (self.bars[tabaroundbarsindices[i]][-1] < mini)):
                            tabaroundbarsindices[i] = tabaroundbarsindices[i] + 1
                        if ((tabaroundbarsindices[i] == nbBars) or (self.bars[tabaroundbarsindices[i]][:-2] > tabaroundpositions[i])):
                            totalborder = True
                            partialborder = True
                            if alreadycut :
                                bordergrid.addBar(self.bars[barsindex][:-2], remember, self.bars[barsindex][-1])
                                alreadycut = False
                            else : 
                                bordergrid.addBar(self.bars[barsindex][:-2], self.bars[barsindex][-2], self.bars[barsindex][-1])
                            barsindex = barsindex + 1          
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
                        elif (self.bars[tabaroundbarsindices[i]][-2] > maxi):
                            mini = self.bars[tabaroundbarsindices[i]][-2]
                            maxi = self.bars[tabaroundbarsindices[i]][-1]
                            i =0
                        else :
                            mini = max(self.bars[tabaroundbarsindices[i]][-2],mini)
                            maxi = min(self.bars[tabaroundbarsindices[i]][-1],maxi)
                            i =i+1
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
                            else :
                                mini = self.bars[barsindex][-2]+1
                                maxi = self.intervalNumberperaxis[-1]
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
        grid = BarGridKernel(self.originCoords,self.oppositeCoords,self.intervalNumberperaxis,self.permutation,None,None,data,self.metadata)
        barsindex = 0
        otherbarsindex = 0
        while (barsindex < len(self.bars)) and (otherbarsindex < len(othergrid.bars)):
            actualbarposition = self.bars[barsindex][:-2]
#            print("actualbarposition[0] ::%d " %actualbarposition[0])

            while (otherbarsindex < len(othergrid.bars)) and (othergrid.bars[otherbarsindex][:-2] < self.bars[barsindex][:-2]):
                otherbarsindex = otherbarsindex + 1
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

            while (barsindex < len(self.bars)) and (otherbarsindex < len(othergrid.bars)) and (othergrid.bars[otherbarsindex][:-2] > self.bars[barsindex][:-2]):
                barsindex = barsindex + 1
        return grid                             

    def MinusBarGridKernel(self,othergrid):
        '''
        Returns an instance of BarGridKernel which is the element of the BarGridKernels
        which are not in the other one. The Bargridkernel have the same underlying grid characteristics 
        '''
        data = []
        grid = BarGridKernel(self.originCoords,self.oppositeCoords,self.intervalNumberperaxis,self.permutation,None,None,data,self.metadata)
        barsindex = 0
        otherbarsindex = 0
        while (barsindex < len(self.bars)) and (otherbarsindex < len(othergrid.bars)):
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

    
    @overrides
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
        permutinversepas = np.dot(self.permutation, self.intervalNumberperaxis / (self.oppositeCoords - self.originCoords))
        data = []
        grid = BarGridKernel(newOriginCoords,newOppositeCoords,newIntervalNumberperaxis,self.permutation,None,None,data,self.metadata)
#        oups = 0
#        while (oups < 1) :
#            oups = 1
        while(actualbarposition[0]<permutnewIntervalNumberperaxis[0]+1):
            realpoint = permutnewOriginCoords[:-1] + actualbarposition * permutnewpas[:-1]
            intpoint = (realpoint-permutOriginCoords[:-1]) * permutinversepas[:-1]
            intpoint = [int(e+0.5) for e in intpoint]
            while (barsindex < len(self.bars)) and (self.bars[barsindex][:2] < intpoint):
                barsindex = barsindex+1
            barinprocess = False
#            print intpoint
            while (barsindex < len(self.bars)) and (self.bars[barsindex][:-2] == intpoint):
                inf = self.bars[barsindex][-2]
                realinf = inf/permutinversepas[-1] +permutOriginCoords[-1]
                intinf = int((realinf-permutnewOriginCoords[-1])/permutnewpas[-1]+0.5)
                sup = self.bars[barsindex][-1]
                realsup = sup/permutinversepas[-1] +permutOriginCoords[-1]
                intsup = int((realsup-permutnewOriginCoords[-1])/permutnewpas[-1]+0.5)
#                print realinf
#                print realsup
#                print intinf
#                print intsup

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
        # First, we collect the bars already present at the position 'coords'
        # and we merge the bar to add with the existing ones
        # two bars will be merged if at least they touch themselves
        # "touch" means that a lower bound of one bar is equals to the (upper bound of the other one) + 1
        insertion_point = self.bars.bisect(coords)
        merged = False
        mergedBarsToRemove=[]
        rightExpanded = False
        while insertion_point<len(self.bars) and self.bars[insertion_point][:-2]==coords:
            if inf > self.bars[insertion_point][-1] + 1:
                # the new bar doesn't touch the right of the current one
                # we should test if it isn't equals to the upper bound + 1 to ensure that it doesn't touch
                insertion_point += 1
                continue;
            if rightExpanded:
                # a previous bar has been modified, we check that it doesn't cross or touch the current bar
                if self.bars[insertion_point][-2] <= self.bars[insertion_point-1][-1] + 1:
                    # the previous bar now intersects the lower bound of the current one
                    # so let's merge the two bars
                    self.bars[insertion_point][-2] = self.bars[insertion_point-1][-2]
                    if self.bars[insertion_point][-2] <= self.bars[insertion_point-1][-2]:
                        # the previous bar completly overlaps the current one
                        self.bars[insertion_point][-2] = self.bars[insertion_point-1][-2]
                        mergedBarsToRemove.append(insertion_point-1)
                        rightExpanded = True
            elif inf >= self.bars[insertion_point][-2] and inf <= self.bars[insertion_point][-1] + 1:
                # the lower bound of the inserted bar is inside the current one
                merged = True
                if sup > self.bars[insertion_point][-1]:
                    # the upper bound is outside the current bar, so we update the upper bound
                    self.bars[insertion_point][-1] = sup
                    rightExpanded = True
            elif inf < self.bars[insertion_point][-2]:
                # the lower bound of the inserted bar is before the current one
                if sup >= self.bars[insertion_point][-2] - 1:
                    # the inserted bar crosses or touches the current bar, so we update the lower bound
                    self.bars[insertion_point][-2] = inf
                    merged = True
                    if sup > self.bars[insertion_point][-1]:
                        # the inserted bound is globally bigger than the current one, so we update also the upper bound
                        self.bars[insertion_point][-1] = sup
                        rightExpanded = True
            insertion_point += 1
        for index in reversed(mergedBarsToRemove):
            del self.bars[index]
        if not merged:
            self.bars.add(coords[:] + [inf,sup])
        self.kernelMinPoint[:-1] = [min(x) for x in zip(self.kernelMinPoint[:-1],coords)]
        self.kernelMinPoint[-1] = min(self.kernelMinPoint[-1], inf)
        self.kernelMaxPoint[:-1] = [max(x) for x in zip(self.kernelMaxPoint[:-1],coords)]
        self.kernelMaxPoint[-1] = max(self.kernelMaxPoint[-1], sup)
      
    def getBars(self):
        return self.bars

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
        point_int = np.dot(self.permutation, np.transpose(point_int))
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
                if point[:-1] == bar[:-2]:
                    # we have reached the interesting zone
                    candidateBar = True
                    # is our point in the bar?
                    if (point[l-1] >= bar[l-1]-0.5) and (point[l-1] <= bar[l] + 0.5):
                        result = True
                        break
                elif candidateBar:
                    # we have passed the position in (n-1) dimensions space, so we can't find candidates anymore
                    break
        return result

    def permute(self,permutation):
      '''
      Create a BarGrid corresponding to the same data as the initial one but with a different permutation of the variables :  np.dot(np.transpose(permutation),self.permutation)
      instead of self.permutation
      ''' 
        
      griddata = []
      unitbars = []
      dimension = len(self.originCoords)
      matid = np.identity(dimension,dtype = int)
      b = False
      for i in range(dimension):
        for j in range(dimension):
            if permutation[i][j] != matid[i][j]:
                b = True
      if b: 
	  permutegrid = BarGridKernel(self.originCoords,self.oppositeCoords,self.intervalNumberperaxis,np.dot(np.transpose(permutation),self.permutation),np.dot(np.transpose(permutation),self.kernelMinPoint),np.dot(np.transpose(permutation),self.kernelMaxPoint),griddata,self.metadata)

          if permutation[dimension-1][dimension-1] == 0:
	        barposition = [0]*(dimension-1)
	        increment = [0]*len(barposition)
	        increment.append(1)
	        oldincrement = list(np.dot(permutation,np.array(increment,int)))[:-1]
		oldindex = oldincrement.index(1)
	        newincrement = list(np.dot(np.transpose(permutation),np.array(increment,int)))[:-1]
		newindex = newincrement.index(1)
	        NmaxUsefullBars = list(np.dot(self.permutation, self.intervalNumberperaxis))[oldindex]
	        barposition.append(0)

	        permutnewIntervalNumberperaxis = np.dot(permutegrid.permutation, permutegrid.intervalNumberperaxis)
	        if (newindex == 0):
	            indexbar = 1
	        else :
	            indexbar = 0

	        if dimension == 2:        
	#	            print "barposition"
	#	            print barposition   
		            usefuloldbars = []
		            newbars = []
		            oldbarposition = list(np.dot(permutation,np.array(barposition,int)))[:-1]
		            for i in range(NmaxUsefullBars+1):
		                oldbarposition[oldindex] = i
	#	                print oldbarposition
		                insertion_point = self.bars.bisect(oldbarposition)
		                while insertion_point<len(self.bars) and self.bars[insertion_point][:-2]==oldbarposition:
		                    usefuloldbars.append(self.bars[insertion_point])
		                    insertion_point = insertion_point+1
	#	            print usefuloldbars        
		            
		            for oldbar in usefuloldbars:
	#	                print "newoldbar"
	#	                print oldbar
		                level = oldbar[oldindex]
		                unitbar = barposition[:-1] + [level,level]
		                mini = oldbar[-2]
		                maxi = oldbar[-1]
		                newbartoupdateindex = mini 
		                if newbars:
		                    k = 0                
		                    while k <len(newbars):
		                        newbar = newbars[k]
	#	        		print "ole"
	#	                        print newbars
	#			        print newbar
	#	                        print k
		                        if (newbar[newindex] > maxi):
		                            break
		                        elif (newbar[newindex] >= mini):
	#		            	    print newbar[newindex]
		                            if (newbar[newindex] > newbartoupdateindex):
		                                for l in range(newbartoupdateindex,newbar[newindex]):
						    unitbar[newindex] = l                                
						    newbars.insert(k,copy.copy(unitbar))
		                                    k=k+1
		                                newbartoupdateindex = newbar[newindex]  
		                            if (newbar[-1] == level-1):
		                                newbar[-1] = level
		                                newbartoupdateindex = newbar[newindex]+1
		                        k = k+1  
		                    for l in range(newbartoupdateindex,maxi+1):
				        unitbar[newindex] = l                                
				        newbars.insert(k,copy.copy(unitbar))
		                        k = k+1
		                else :
		                    for l in range(mini,maxi+1):
				        unitbar[newindex] = l                                
				        newbars.append(copy.copy(unitbar))
	#	            print "newbars" 
	#	            print newbars                        
		            permutegrid.bars.update(newbars)
	                    
	        else:
		        while(barposition[indexbar]<permutnewIntervalNumberperaxis[indexbar]+1):
	#	            print "barposition"
	#	            print barposition   
		            usefuloldbars = []
		            newbars = []
		            oldbarposition = list(np.dot(permutation,np.array(barposition,int)))[:-1]
		            for i in range(NmaxUsefullBars+1):
		                oldbarposition[oldindex] = i
	#	                print oldbarposition
		                insertion_point = self.bars.bisect(oldbarposition)
		                while insertion_point<len(self.bars) and self.bars[insertion_point][:-2]==oldbarposition:
		                    usefuloldbars.append(self.bars[insertion_point])
		                    insertion_point = insertion_point+1
	#	            print usefuloldbars        
		            
		            for oldbar in usefuloldbars:
	#	                print "newoldbar"
	#	                print oldbar
		                level = oldbar[oldindex]
		                unitbar = barposition[:-1] + [level,level]
		                mini = oldbar[-2]
		                maxi = oldbar[-1]
		                newbartoupdateindex = mini 
		                if newbars:
		                    k = 0                
		                    while k <len(newbars):
		                        newbar = newbars[k]
	#	        		print "ole"
	#	                        print newbars
	#			        print newbar
	#	                        print k
		                        if (newbar[newindex] > maxi):
		                            break
		                        elif (newbar[newindex] >= mini):
	#		            	    print newbar[newindex]
		                            if (newbar[newindex] > newbartoupdateindex):
		                                for l in range(newbartoupdateindex,newbar[newindex]):
						    unitbar[newindex] = l                                
						    newbars.insert(k,copy.copy(unitbar))
		                                    k=k+1
		                                newbartoupdateindex = newbar[newindex]  
		                            if (newbar[-1] == level-1):
		                                newbar[-1] = level
		                                newbartoupdateindex = newbar[newindex]+1
		                        k = k+1  
		                    for l in range(newbartoupdateindex,maxi+1):
				        unitbar[newindex] = l                                
				        newbars.insert(k,copy.copy(unitbar))
		                        k = k+1
		                else :
		                    for l in range(mini,maxi+1):
				        unitbar[newindex] = l                                
				        newbars.append(copy.copy(unitbar))
	#	            print "newbars" 
	#	            print newbars                        
		            permutegrid.bars.update(newbars)
		             
		            for i in range(dimension-1):
		                if ((dimension-2-i) != newindex):
		                    if ((i == dimension - 2- indexbar) or (barposition[dimension-2-i]<permutnewIntervalNumberperaxis[dimension-2-i])):
		                        barposition[dimension-2-i] = barposition[dimension-2-i]+1
		                        break
		                    else :
		                        barposition[dimension-2-i] = 0
          else:
              for bar in self.bars :
                  tpermutation = np.transpose(permutation)
                  permutegrid.bars.add(list(np.dot(tpermutation,bar[:-1]))+[bar[-1]])
      else:
          permutegrid = BarGridKernel(self.originCoords,self.oppositeCoords,self.intervalNumberperaxis,np.dot(np.transpose(permutation),self.permutation),np.dot(np.transpose(permutation),self.kernelMinPoint),np.dot(np.transpose(permutation),self.kernelMaxPoint),list(self.bars),self.metadata)
      return permutegrid


    def buildNewBars(self,barposition,permutation,data):
        newdata = []
        unitbar = []
        increment = [0]*len(barposition)
        increment.append(1)
        newincrement = list(np.dot(np.transpose(permutation),np.array(increment,int)))[:-1]
	newindex = newincrement.index(1)
        oldincrement = list(np.dot(permutation,np.array(increment,int)))[:-1]
	oldindex = oldincrement.index(1)

        NmaxNewBars = list(np.dot(self.permutation, self.intervalNumberperaxis))[-1]
#        print newincrement
#        print newindex
#        print oldincrement
#        print oldindex

#        print NmaxNewBars
        
        for oldbar in data:
            level = oldbar[oldindex]
            unitbar = barposition + [level,level]
            mini = oldbar[-2]
            maxi = oldbar[-1]
            newbartoupdateindex = mini 
            if newdata:                
                for k in range(len(newdata)):
#		    print "ole"
#                    print newdata
#		    print k
                    newbar = newdata[k]    
                    if (newbar[newindex] >= mini) and (newbar[newindex] <= maxi):
#			print newbar[newindex]
                        if (newbar[newindex] > newbartoupdateindex):
                            for l in range(newbartoupdateindex,newbar[newindex]):
				unitbar[newindex] = l                                
				newdata.insert(k,copy.copy(unitbar))
                                k=k+1  
                        if (newbar[-1] == level-1):
                            newbar[-1] = level
                            newbartoupdateindex = newbar[newindex]+1 
                for l in range(newbartoupdateindex,maxi+1):
		    unitbar[newindex] = l                                
		    newdata.insert(len(newdata),copy.copy(unitbar))
            else :
                for l in range(mini,maxi+1):
		    unitbar[newindex] = l                                
		    newdata.append(copy.copy(unitbar))
                                    
        return newdata

    def findUsefullBars(self,barposition,permutation):
        data = []
        increment = [0]*len(barposition)
        barposition.append(0)
        increment.append(1)
        oldincrement = list(np.dot(permutation,np.array(increment,int)))[:-1]
	index = oldincrement.index(1)
        oldbarposition = list(np.dot(permutation,np.array(barposition,int)))[:-1]
        NmaxUsefullBars = list(np.dot(self.permutation, self.intervalNumberperaxis))[index]
#        print oldbarposition
#        print oldincrement
#        print index
#        print NmaxUsefullBars

        for i in range(NmaxUsefullBars+1):
            oldbarposition[index] = i
            insertion_point = self.bars.bisect(oldbarposition)
#            print oldbarposition
#            print insertion_point
            while insertion_point<len(self.bars) and self.bars[insertion_point][:-2]==oldbarposition:
                data.append(self.bars[insertion_point])
                insertion_point = insertion_point+1
        return data


if __name__ == "__main__":
    #grid = BarGridKernel([0,0,0], [1,1,1])
    #grid.addBar([1,2],3,4)
    #grid.addBar([2,2],2,4)
    #grid.addBar([2,3],3,4)
    #grid.writeHDF5('test.h5')
  
    import time
    import timeit
    import sys
    import FileFormatLoader
    
    startTime = time.time()
    grid = FileFormatLoader.PspModifiedLoader().read('../samples/2D_light.txt')

    total = grid.getTotalPointNumber()  
    print("grid totalpoint ::%d " % total)

    readTime = time.time() - startTime
    print(('reading raw txt in {:.2f}s'.format(readTime)))
    print("minPoint ::%d " % grid.kernelMinPoint[0])
    print("maxPoint ::%d " % grid.kernelMaxPoint[0])

    print(grid.originCoords)
    print(grid.oppositeCoords)
    print(grid.intervalNumberperaxis)
    
    distancegriddimensions = [1001, 1001]
    distancegridintervals = [e-1 for e in distancegriddimensions]
    
    resizebargrid = grid.toBarGridKernel(grid.originCoords, grid.oppositeCoords, distancegridintervals)
#  print resizebargrid.bars

    from hdf5common import HDF5Manager
    hm = HDF5Manager([BarGridKernel])
#  startTime = time.time()
#  regularGrid = grid.toRegularGridKernel()
#  readTime = time.time() - startTime
#  print('converting to grid in {:.2f}s'.format(readTime))

    permutation = np.array([[0,1],[1,0]])
    permutgrid = grid.permute(permutation)
    permutgrid2 = permutgrid.permute(np.transpose(permutation))

    '''
    barposition = [1,0]
#    permutation = np.array([[1,0,0],[0,0,1],[0,1,0]])
    permutation = np.array([[0,0,1],[1,0,0],[0,1,0]])
    grid.originCoords = np.array([1,2,3])
    grid.kernelMinPoint = np.array([0,0,1])
    grid.kernelMaxPoint = np.array([1,2,20])

    grid.permutation = np.array([[1,0,0],[0,1,0],[0,0,1]])
    grid.intervalNumberperaxis = np.array([2,4,22]) 
    grid.bars = SortedList([[0,0,4,7],[0,1,3,8],[0,1,13,18],[0,2,6,7],[0,3,3,8],[1,0,4,19],[1,1,1,9],[1,1,12,20],[1,2,6,17],[1,3,3,18]])
#    usefullbars = grid.findUsefullBars(barposition,permutation)
#    barposition = [1,0]
#    newbars = grid.buildNewBars(barposition,permutation,usefullbars)
#    barposition = [1,0]
    permutgrid = grid.permute(permutation)
    permutgrid2 = permutgrid.permute(np.transpose(permutation))
    '''        
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

  
 