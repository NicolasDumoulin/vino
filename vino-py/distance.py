# -*- coding: utf-8 -*-
from BarGridKernel import BarGridKernel


class Line(object):
    def __init__(self, data = []):
        self.data = data 
            
    def getLineFromMatrix(self,matrix,positions):
        for i in range(len(positions)):
            self.data[i] = matrix.data[positions[i]]    


    def firstpass(self,lowborder,upborder):
        lendata = len(self.data)        
        if lowborder:
            self.data[0] = 1
        for i in range(1,lendata):
            self.data[i] = min(self.data[i],self.data[i-1]+1)
        if upborder:
            self.data[lendata-1] = 1
        for i in range(1,lendata):
            self.data[lendata-1-i] = min(self.data[lendata-1-i],self.data[lendata-i]+1)
        for i in range(lendata):
            self.data[i] = self.data[i]*self.data[i]
        
        
    def update(self,norm,lowborder,upborder):
        tabindices = []
        tab = list(self.data)
        if lowborder == True:
            tab.insert(0,0)
        if upborder == True:
            tab.append(0)
        lentab = len(tab)
        for i in range(lentab):
            tabindices.append(0)
        
        for j in range(1,lentab):
 #           print "new j %d" %j
 #           print tabindices
            i = tabindices[-1]
            maxrange = lentab-1            
            while (i>=0):
#                print i
#                print j
#                print tab[i]
#                print tab[j]
                intersect = norm.intersectindex(i,j,tab[i],tab[j])
#                print "intersect %d" %intersect
                if (intersect > maxrange):
                    i = -1
#                    print "sortie 1"
                elif (intersect < 0):
                    k = maxrange
                    while (k>=0) and (tabindices[k] == i) :
                        tabindices[k] = j
                        k = k-1
                    if k >=0:
                        i = tabindices[k]
                        maxrange = k
#                        print "sortie 2"
                    else :
                        i = -1
#                        print "sortie 3"
                elif (tabindices[intersect] == i) :
                    for k in range(intersect,maxrange+1):
                        tabindices[k] = j
                    i = - 1
#                    print "sortie 4"
                else : 
                    k = maxrange
#                    print tabindices
                    while (k>=0) and (tabindices[k] == i) :
                        tabindices[k] = j
                        k = k-1
#                    print tabindices
                    if k >=0:
                        i = tabindices[k]
                        maxrange = k
#                        print i
#                        print "sortie 5"
                    else :
                        i = -1
#                        print "sortie 6"
 #       print tabindices
#        print self.data
        if lowborder == True:
            indexadd = 1
        else : 
            indexadd = 0
        for k in range(len(self.data)):
#            print k
            kbis = k+indexadd
            index = tabindices[kbis]
            self.data[k] = norm.newdistance(tab[index],kbis-index)            
#        print self.data
        
class EucNorm(object):
    def __init__(self, normname = "euclidean"):
        self.name = normname   
        
    def intersectindex(self,i,j,disti,distj):
        index = 1 + (j*j - i*i + distj - disti)//(2*(j - i))
        return index
        
    def newdistance (self,olddistance, gap):
        newdist = olddistance + gap*gap                
        return newdist
        
class Matrix(object):
    def __init__(self, dimensions = [], data = []):
        self.dimensions = map(lambda e: int(e), dimensions)
        self.data = data
    
    @classmethod 
    def initFromBarGridKernel(cls,bargrid):
        newmatrix = None
        dimensions = list(bargrid.intervalNumberperaxis)
        dimensions = map(lambda e: e+1, dimensions)
        maxdim = int(max(dimensions))
        nbdim = len(dimensions)
#        print dimensions
        total = 1
        for i in range(nbdim):
            total = total*dimensions[i]
        data = [0]*total
        newmatrix = cls(dimensions,data)
        spacesizes = [1]*nbdim
#        print newmatrix.dimensions
#        print total
        for i in range(1,nbdim):
            spacesizes[nbdim-1-i] = spacesizes[nbdim-i]*dimensions[nbdim-i]
#        print spacesizes
        for bar in bargrid.bars:
            position = 0
            for i in range(nbdim-1):
                position = position + spacesizes[i]*bar[i]         
            for i in range(int(bar[-2]),int(bar[-1]+1)):
                newmatrix.data[int(position) + i] = maxdim
        return newmatrix

    def toDataPointDistance(self):
        data = []
        nbdim = len(self.dimensions)
        point = [0]*(nbdim+1)
        for position in range(len(self.data)):
            if self.data[position] > 0:
                point[-1] = self.data[position]
                data.append(list(point))
#                data.append(list(point).append(self.data[position]))
#            print position
#            print point
            
            for i in range(nbdim):
                if (point[nbdim-1-i] < self.dimensions[nbdim-1-i]-1):
                    point[nbdim-1-i] = point[nbdim-1-i]+1
                    break
                else : 
                    point[nbdim-1-i] = 0
        return data
        
    def totalpointNumber(self):
        total = 1
        for i in range(len(self.dimensions)):
            total = total*self.dimensions[i]
        return total
        
    def spaceSize(self,direction):
        spacesize = 1
        lendimension = len(self.dimensions)
        i = 0
        while i < (lendimension-direction):
            spacesize = spacesize * self.dimensions[lendimension-1-i]
            i = i+1
        return spacesize
        
    def initPosition(self,direction):
        positions = []
        position = 0
        spacesize = self.spaceSize(direction)
        for i in range(self.dimensions[direction-1]):
            positions.append(position)
            position = position + spacesize
        return positions
   
    def initLine(self,direction):
        line = Line(data = [])
        for i in range(self.dimensions[direction-1]):
            line.data.append(0)
        return line
        
    def writeFromLine(self,line,positions):
        for i in range(len(positions)):
            self.data[positions[i]] = line.data[i]
        
        
    def distance(self,norm,lowborders,upborders):
        for direction in range(1,len(self.dimensions)+1):
#            print "new direction"
            spacesize = self.spaceSize(direction)    
            positions = self.initPosition(direction)
            line = self.initLine(direction)
#            print line.data
            i = 0
            if direction ==1:
                for i in range(spacesize):
#                    print i                    
                    line.getLineFromMatrix(self,positions)
#                    print positions
#                    print line.data
                    line.firstpass(lowborders[direction - 1],upborders[direction - 1])
                    self.writeFromLine(line,positions)
#                    print line.data
#                    print positions
                    positions = map(lambda e: e+1, positions)

            else :
                spacesizeup = self.spaceSize(direction-1)    
                for i in range(self.totalpointNumber()/spacesizeup):
#                    print i                    
                    for j in range(spacesize): 
                        line.getLineFromMatrix(self,positions)
#                        print positions
#                        print "line"
#                        print line.data
                        line.update(norm,lowborders[direction - 1],upborders[direction - 1])
                        self.writeFromLine(line,positions)
                        positions = map(lambda e: e+1, positions)
                    positions = map(lambda e: e-spacesize+spacesizeup, positions)

'''
                spacesizeup = self.spaceSize(direction-1)    
                while (i < (self.totalpointNumber()/self.dimensions[direction-1])):
                    print i                    
                    j = 0
                    while (j<spacesize) : 
                        line.getLineFromMatrix(self,positions)
#                        print positions
#                        print "line"
#                        print line.data
                        line.update(norm,lowborders[direction - 1],upborders[direction - 1])
                        self.writeFromLine(line,positions)
                        i = i + 1
                        j = j+ 1
                        positions = map(lambda e: e+1, positions)
                    positions = map(lambda e: e-spacesize+spacesizeup, positions)
'''        
        

if __name__ == "__main__":
    
    import time
    
    norm = EucNorm()
   
#    bargrid = BarGridKernel([0,0], [10,10], [10,10])
#    bargrid.addBar([1],3,7)
#    bargrid.addBar([2],5,5)
#    bargrid.addBar([3],0,10)
    bargrid = BarGridKernel.readPatrickSaintPierrebis('../samples/2D_light.txt')
    distancegriddimensions = [2001,2001]
    distancegridintervals = map(lambda e: e-1, distancegriddimensions)
    print "of"    
    print distancegridintervals
    
    resizebargrid = bargrid.toBarGridKernel(bargrid.originCoords, bargrid.oppositeCoords, distancegridintervals)

#    print resizebargrid.bars  101 0.17 s ; 1001 114 s

    distancegrid = Matrix.initFromBarGridKernel(resizebargrid)
    
   
    lowborders = []    
    upborders = []    
    for i in range(len(distancegrid.dimensions)):
      lowborders.append(False)
      upborders.append(False)

    startTime = time.time()
    distancegrid.distance(norm,lowborders,upborders)
    readTime = time.time() - startTime
    print('distance in {:.2f}s'.format(readTime))
  
    data = distancegrid.toDataPointDistance()
    
'''
    data = []
    dim1 = 1000
    dim2 = 1000
    for i in range(dim1):
        for j in range(dim2):
            if ((i-500)*(i-500)+(j-500)*(j-500))<=90000 :
                data.append(max(dim1,dim2))
            else :
                data.append(0)
    
    matrix = Matrix([dim1,dim2],data)
#    print matrix.data
    lowborders = []    
    upborders = []    
    for i in range(len(matrix.dimensions)):
      lowborders.append(False)
      upborders.append(False)
    
    startTime = time.time()
    matrix.distance(norm,lowborders,upborders)
    readTime = time.time() - startTime
    print('distance in {:.2f}s'.format(readTime))

#    for i in range(100):
#        print matrix.data[i*100:(i+1)*100-1]
        
'''

'''
    for direction in range(1,len(matrix.dimensions)+1):
        print "new direction"
        spacesize = matrix.spaceSize(direction)    
        positions = matrix.initPosition(direction)
        line = matrix.initLine(direction)
        print line.data
        i = 0
        if direction ==1:
            while (i < spacesize):
                    line.getLineFromMatrix(matrix,positions)
                    print positions
                    print line.data
                    line.firstpass(False,False)
                    matrix.writeFromLine(line,positions)
                    print line.data
                    print positions
                    i = i + 1
                    positions = map(lambda e: e+1, positions)
            print matrix.data

        else :
            spacesizeup = matrix.spaceSize(direction-1)    
            while (i < (matrix.totalpointNumber()/matrix.dimensions[direction-1])):
                j = 0
                while (j<spacesize) : 
                    line.getLineFromMatrix(matrix,positions)
                    print positions
                    print "line"
                    print line.data
                    line.update(norm,False,False)
                    matrix.writeFromLine(line,positions)
                    i = i + 1
                    j = j+ 1
                    positions = map(lambda e: e+1, positions)
                positions = map(lambda e: e-spacesize+spacesizeup, positions)
            print matrix.data
'''