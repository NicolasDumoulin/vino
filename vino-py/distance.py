# -*- coding: utf-8 -*-
from BarGridKernel import BarGridKernel


class Line(object):
    '''
	The algorithm used to evaluate the distance map in the Matrix class uses what we call Line which gathers the values when one coordinate varies and the n-1 others are fixed
	The algorithm has an initialization phase (the method firstpass below) and n-1 iteration of method update.
    '''
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
    '''
    This class is designed to describe the norm from which the distance is computed. In the algorithm of distance evaluation (distance method of Matrix class below), 
    two charactéristics depending on the norm are used : a method to evaluate the intersection index and a method to evaluate the distance on i dimensions from the distance 
    on i-1 dimensions and the distance in the ith dimension.
    For the moment only the characteristics corresponding to the Euclidean norm are implemented below.
    ''' 
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
	self.maximum = max(data)    	

    @classmethod 
    def initFromBarGridKernel(cls,bargrid):
	'''
	Initialize from a BarGridKernel a Matrix with the same underlying grid. The value of the Matrix cell is set at 0 if this cell does'nt belong to the BarGridKernel 
	and to +infty otherwise.
	''' 
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
	newmatrix.maximum = max(newmatrix.data)
        return newmatrix

    def toDataPointDistance(self):
	'''
	Return the list of points coordinates concatenated with their associated non null distance value
	'''
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
	'''
	Return the cell number of the Matrix
	'''
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
            self.maximum = max(self.data)	
        
    def histogramFromBarGrid(self,bargrid,barnum,maxdistance):
	barlimits = []
	barlimits.append(0)
	occurnumber = []
	occurnumber.append(0)
        histodict = {}
        if (maxdistance>0) :
            barnumber = barnum-1
	    interval = (maxdistance-1)/float(barnumber)
            for i in range(barnumber+1):
		barlimits.append(int(round(1+i*interval)))
		occurnumber.append(0)
                histodict[str(int(round(1+i*interval)))] = 0
            nbdim = len(self.dimensions)
            spacesizes = [1]*nbdim
	    for i in range(1,nbdim):
                spacesizes[nbdim-1-i] = spacesizes[nbdim-i]*self.dimensions[nbdim-i]
            for bar in bargrid.bars:
                position = 0
                for i in range(nbdim-1):
                    position = position + spacesizes[i]*bar[i]         
                for i in range(int(position)+int(bar[-2]),int(position)+int(bar[-1]+1)):
                    k = 0		
	            for j in range(1,barnumber+2):
	                if (self.data[i]>= barlimits[j]) :
                            k = k+1
		    occurnumber[k]=occurnumber[k]+1
	    histodict = dict(zip(range(barnumber+2),zip(barlimits,occurnumber)))
	else :
	    histodict['0'] = self.totalpointNumber()
	    occurnumber[0] = self.totalpointNumber()
        return histodict

    def histogram(self,barnum,maxdistance):
	barlimits = []
	barlimits.append(0)
	occurnumber = []
	occurnumber.append(0)
        histodict = {}
        if (maxdistance>0) :
            barnumber = barnum-1
            interval = (maxdistance-1)/float(barnumber)
            for i in range(barnumber+1):
		barlimits.append(int(round(1+i*interval)))
		occurnumber.append(0)
                histodict[str(int(round(1+i*interval)))] = 0
	    for i in range(self.totalpointNumber()):
                k = 0		
		for j in range(1,barnumber+2):
	            if (self.data[i]>= barlimits[j]) :
                        k = k+1
		occurnumber[k]=occurnumber[k]+1
	    histodict = dict(zip(range(barnumber+2),zip(barlimits,occurnumber)))
	else :
	    histodict['0'] = self.totalpointNumber()
	    occurnumber[0] = self.totalpointNumber()
        return histodict

if __name__ == "__main__":
    
    import time
    
    norm = EucNorm()
   
#    bargrid = BarGridKernel([0,0], [10,10], [10,10])
#    bargrid.addBar([1],3,7)
#    bargrid.addBar([2],5,5)
#    bargrid.addBar([3],0,10)
    bargrid = BarGridKernel.readPatrickSaintPierrebis('../samples/2D_light.txt')
    distancegriddimensions = [31,31]#[2001,2001]
    distancegridintervals = map(lambda e: e-1, distancegriddimensions)
    print "of"    
    print distancegridintervals

    startTime = time.time()
    resizebargrid = bargrid.toBarGridKernel(bargrid.originCoords, bargrid.oppositeCoords, distancegridintervals)
    readTime = time.time() - startTime

    print('resize in {:.2f}s'.format(readTime))
    '''
    resizebargrid2 = bargrid.toBarGridKernel(bargrid.originCoords, bargrid.oppositeCoords, distancegridintervals)
    for bar in resizebargrid2.bars:
        bar[1]=bar[1]+1
        bar[2]=bar[2]-1

    minusgrid12 = resizebargrid.MinusBarGridKernel(resizebargrid2)

    '''
#    print resizebargrid.bars  101 0.17 s ; 1001 114 s
    startTime = time.time()
    distancegrid = Matrix.initFromBarGridKernel(resizebargrid)
    readTime = time.time() - startTime

    print('init distance in {:.2f}s'.format(readTime))

    
    
    lowborders = []    
    upborders = []    
    for i in range(len(distancegrid.dimensions)):
      lowborders.append(False)
      upborders.append(False)

    startTime = time.time()
    distancegrid.distance(norm,lowborders,upborders)
    readTime = time.time() - startTime
    print('distance in {:.2f}s'.format(readTime))
  
#    data = distancegrid.toDataPointDistance()

    startTime = time.time()
    histo = distancegrid.histogram(12, 44)#distancegrid.maximum)    
    readTime = time.time() - startTime
    print('histogram in {:.2f}s'.format(readTime))

    '''
    startTime = time.time()
    histo1 = distancegrid.histogramFromBarGrid(minusgrid12,12,55)#distancegrid.maximum)
    readTime = time.time() - startTime
    print('histogram with bargrid in {:.2f}s'.format(readTime))

    limits=[]
    occurnumber = []
    occurnumber1 = []

    for key in histo.keys():
	limits.append(histo.get(key)[0])
        occurnumber.append(histo.get(key)[1])
	occurnumber1.append(histo1.get(key)[1])

    histoCompar = dict(zip(histo.keys(),zip(limits,occurnumber,occurnumber1)))

#	histo[key].append(histo1.get(key)[1])
    '''

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