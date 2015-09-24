# -*- coding: utf8 -*-

import numpy
from math import floor, ceil
import sys
sys.path.append('../../vino-py')
from RegularGridKernel import RegularGridKernel
from hdf5common import HDF5Manager

def pnext(p, l, dt, b, r, q, m):
	return p+dt*(b*p-l-r*pow(p,q)/(pow(m,q)+pow(p,q)))

def lnext(l, dt, u):
	#print("%f %f %f"%(l,dt,u))
	return l-dt*u

def computeTrajectory(dt):
	if dt<1/nmax: dt=1/nmax
	tabP=numpy.empty(nmax)
	tabL=numpy.empty(nmax)
	tabP[0] = pmax
	tabL[0] = b*pmax-r*pow(pmax,q)/(pow(m,q)+pow(pmax,q))
	i = 0
	while tabP[i]>=0 and tabL[i]<=lmax:
          i+=1
          tabP[i]=pnext(tabP[i-1],tabL[i-1],dt);
          tabL[i]=lnext(tabL[i-1],dt,umax*(-1), b, r, q, m);
	return [i,tabP,tabL]

def computeTrajectoryP(dt, p0, l0, dp, dl, np, nl, umax, nmax, pmax, lmax, b, r, q, m):
	if dt<1/nmax: dt=1/nmax
	tabP=numpy.empty(nmax)
        firstP = pmax
        firstL = b*pmax-r*pow(pmax,q)/(pow(m,q)+pow(pmax,q))
        #print("{:g} {:g}".format(firstL,firstP))
        # the column indix on the grid just after the start point (l,p)
        gridI = int(ceil((firstL-l0)/dl))
        firstCol = gridI
        # stepping until the first value in the next grid column
        for i in range(int(ceil((gridI*dl+l0-firstL)/(dt*umax)))):
          firstP = pnext(firstP, firstL, dt, b, r, q, m)
          firstL = firstL + dt*umax
          #print("{:g} {:g}".format(firstL,firstP))
        # nb steps of L in a same grid column
        nbSteps = int(floor(dl/(dt*umax)))
        # for each step i of L on the grid, we will store the interpolated value of P
	i = 0
	while firstP>=0 and firstL<=lmax:
          if i>0:
            # stepping until the last point of the trajectory before a new step on the L axis of the grid
            for j in range(nbSteps-1):
              firstP = pnext(firstP, firstL, dt, b, r, q, m)
              firstL = firstL + dt*umax
              #print("{:g} {:g}".format(firstL,firstP))
          # we've reached the last point on the trajectory in the current grid column
          previousP = firstP
          previousL = firstL
          # getting the following point
          firstP = pnext(firstP, firstL, dt, b, r, q, m)
          firstL = firstL + dt*umax
          #print("{:g} {:g}".format(firstL,firstP))
          # value of L on the grid
          gridL = l0 + dl*gridI
          # we can interpolate the value of P on the grid from the two points of the trajectory
          tabP[i] = previousP + (firstP-previousP)*(gridL-previousL)/(firstL-previousL)
          # TODO store the index of P in the grid instead of the value
          gridI+=1
          i+=1
	tabP.resize(i,refcheck=False)
	return firstCol,tabP
 
def writeHDF5_coords(rgk, filename, **datasets_options):
  from hdf5common import HDF5Writer
  with HDF5Writer(filename) as w:
    w.writeMetadata({'problem':[["name","foo"]], 'algorithm':[["name","greatAlgo"]]})
    coords_list = [[i,j] for i,row in enumerate(rgk.grid) for j,e in enumerate(row) if e]
    w.writeData(coords_list, {
      'origin' : rgk.originCoords,
      'steps' : rgk.dimensionsSteps,
      'format' : rgk.getFormatCode()
        }, **datasets_options)
          

def writeViablesPointsHDF5(filename, dt, p0, l0, dp, dl, np, nl):
  with open(filename+".txt", 'w') as f:
    f.write("Pas de temps : {:f}\n".format(dt))
    firstCol,tabp = computeTrajectoryP(dt, p0, l0, dp, dl, np, nl, umax, nmax, pmax, lmax, b, r, q, m)
    iLmin=ceil((lmin-l0)/dl)
    iLmax=floor((lmax-l0)/dl)
    iPmax=floor(pmax/dp)
    grid=numpy.array([
      i>=iLmin and i<=iLmax and j<=iPmax and
        (i<firstCol or (i<firstCol+len(tabp) and p0+j*dp<=tabp[i-firstCol]))
      for i in numpy.arange(nl) for j in numpy.arange(np)
      ]).reshape(np,nl)
    rgk = RegularGridKernel([p0,l0],[dp,dl])
    rgk.setGrid(grid)
    for i in range(nl):
      for j in range(np):
        if grid[i,j]:
          f.write("{:f} {:f}\n".format(l0+i*dl,p0+j*dp))
  HDF5Manager.writeKernel(rgk, filename+".h5", compression="gzip", compression_opts=9)
  writeHDF5_coords(rgk, filename+"_coords.h5", compression="gzip", compression_opts=9)

if __name__ == "__main__":
	b, m, q, r, umax = [0.8, 1, 8, 1, 0.1]
	pmax, lmin, lmax = [1.4, 0.1, 1]
	nmax = 10000
	p0, l0, dp, dl, np, nl = [ 0, 0.1, 0.001, 0.001, 1000, 1000]
	dt = 0.001
	
	writeViablesPointsHDF5("lake_py", dt, p0, l0, dp, dl, np, nl)

	