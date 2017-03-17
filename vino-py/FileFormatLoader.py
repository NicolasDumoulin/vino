# -*- coding: utf-8 -*-

import abc

class FileFormatException(Exception):
    '''
    This exception is raised when an syntax error occurs while trying to read a file.
    '''
    pass

import logging

class Loader(object):
    def __init__(self):
        self.loaders = [Hdf5Loader(), PspLoader(), PspModifiedLoader(), ViabilitreeLoader()]
    
    def loadersdoc(self):
        for loader in self.loaders:
            print("{0}: {1}".format(type(loader).__name__, str(loader.__doc__)))
    
    def load(self, filename):
        '''
        Load a file by trying all file loaders, and return an object of type Kernel, precisely on of its subtypes.
        Returns None if no suitable loader have succeed to load the file.
        '''
        for loader in self.loaders:
            try:
                return loader.read(filename)
            except Exception as e:
                logging.getLogger(__name__).info("Loading of %s fails with the %s loader: %s",filename, loader, e)
        return None

class FileFormatLoader(object):
    '''
    Abstract class for loaders that implements a specific format parser.
    '''
    
    @abc.abstractmethod
    def readFile(self, f):
        pass
    
    def read(self, filename):
        with open(filename, 'r') as f:
            return self.readFile(f)      

from overrides import overrides
from BarGridKernel import BarGridKernel
from KdTree import KdTree
from hdf5common import HDF5Manager

class Hdf5Loader(FileFormatLoader):
    '''
    Loader for the Vino HDF5 file format.
    '''
    
    def __init__(self, strategies=[BarGridKernel, KdTree]):
        self.hdf5manager = HDF5Manager(strategies) 
    
    @overrides
    def read(self, filename):
        return self.hdf5manager.readKernel(filename)

import re
import numpy as np
import os
import METADATA

class ViabilitreeLoader(FileFormatLoader):
    '''
    Loader for the output format of the software viabilitree.
    The loader assumes that a second file with the path and the same name but
    with the file extension '.txt' provides metadata in the form 'key:value'
    for each line.
    The metadata 'viabilityproblem.statedimension' is mandatory for loading the file.
    '''

    @overrides
    def read(self, filename):
        metadata = {}
        myre = re.compile('^([^:]*):(.*)$')
        with open(os.path.splitext(filename)[0]+'.txt') as f:
            for line in f:
                if not line.startswith('#'):
                    match = myre.match(line)
                    if match:
                        k, v = match.groups()
                        metadata[k.strip().lower()] = v.strip()
        metadata[METADATA.statedimension] = int(metadata[METADATA.statedimension])
        k = KdTree.readViabilitree(filename, metadata)
        return k
    
class PspLoader(FileFormatLoader):
    '''
    Reader for the raw output format of the software of Patrick Saint-Pierre.
    ''' 
    @overrides
    def readFile(self, f):
        metadata=[]
        bgk = None
        f.readline()
        nbDim = re.match('\s*([0-9]*)\s.*',f.readline()).group(1)
        metadata.append([METADATA.dynamicsdescription, f.readline()])
        metadata.append([METADATA.stateconstraintdescription, f.readline()])
        metadata.append([METADATA.targetdescription, f.readline()])
        for i in range(4): f.readline()
        dimensionsSteps = list(map(int, re.findall('[0-9]+', f.readline())))
        for i in range(2): f.readline()
        origin = list(map(int, re.findall('[0-9]+', f.readline())))
        maxPoint = list(map(int, re.findall('[0-9]+', f.readline())))
        for i in range(5): f.readline()
        # ND Why? Why not opposite = maxPoint
        opposite = origin      
        bgk = BarGridKernel(origin, opposite, dimensionsSteps, metadata=metadata)
        # reading until some lines with 'Initxx'
        stop=False
        initxx=False
        # ND Why restrict min/max point to integer position
        bgk.kernelMinPoint = [e//1 for e in origin]
        bgk.kernelMaxPoint = [e//1 for e in maxPoint]
        while not stop:
            line = f.readline()
            if 'Initxx' in line:
                initxx = True
            elif initxx and 'Initxx' not in line:
                stop = True
        # reading bars
        for line in f:
            coords = list(map(int, re.findall('[0-9]+', line)))
            # ND Why convert point to integer position
            coords = [e//1 for e in coords]
            bgk.addBar(coords[2:-2], coords[-2], coords[-1])
            # TODO what is done with modelMetadata and nbDim
        return bgk
        
class PspModifiedLoader(FileFormatLoader):
    '''
    Reader for the modified output format of the software of Patrick Saint-Pierre.
    By "modified", it means that the raw output file has been modified for give easy access to metadata at the begin of the file.
    '''
    
    @overrides
    def readFile(self, f):
        '''
        Returns an object of class BarGridKernel loaded from an output file from the software of Patrick Saint-Pierre.
        '''
        bgk = None
        origin = list(map(float, re.findall('-?\d+\.?\d*', f.readline())))
        dimension = len(origin)
        if dimension == 0 :
            raise FileFormatException("Dimensions must be > 0")
        opposite = list(map(float, re.findall('-?\d+\.?\d*', f.readline())))
        intervalNumber = list(map(int, re.findall('[0-9]+', f.readline())))
        if dimension !=len(opposite) or dimension!=len(intervalNumber):
            raise FileFormatException("Dimensions of metadata mismatch")
        pointSize = list(map(int, re.findall('[0-9]+', f.readline())))
        intervalNumber = [e//pointSize[0] for e in intervalNumber]
        # reading columns headers and deducing permutation of variables
        line = f.readline()
        columnNumbertoIgnore = len(re.findall('empty', line))
        permutVector = list(map(int, re.findall('[0-9]+', line)))
        permutation = np.zeros(dimension * dimension,int).reshape(dimension,dimension)
        for i in range(dimension):
            permutation[i][permutVector[i]-1]=1
        # Ok, creating the container object
        bgk = BarGridKernel(origin, opposite, intervalNumber,permutation)
        # ignoring lines until 'Initxx'
        stop=False
        while not stop:
            line = f.readline()
            if 'Initxx' in line:
                stop = True
        # reading bars
        stop = False
        while not stop:
            # using a while loop, because the for loop seems buggy with django InMemoryUploadedFile reading
            line = f.readline()
            if not line:
                stop = True
            else:
                coords = list(map(int, re.findall('[0-9]+', line)))
                coords = [e // pointSize[0] for e in coords]
                bgk.addBar(coords[columnNumbertoIgnore:-2], coords[-2], coords[-1])
                # TODO what is done with modelMetadata and nbDim
        return bgk


if __name__ == "__main__":
    FORMAT = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
    logging.basicConfig(format=FORMAT)
    logging.getLogger(__name__).setLevel(logging.DEBUG)
    k = Loader().load('pip-requires.txt')
