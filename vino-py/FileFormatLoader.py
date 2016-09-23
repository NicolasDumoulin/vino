# -*- coding: utf-8 -*-

import abc

class FileFormatException(Exception):
    '''
    This exception is raised when an syntax error occurs while trying to read a file.
    '''
    pass

import logging

#TODO howto guess the kdtree format

class Loader(object):
    def __init__(self):
        self.loaders = [Hdf5Loader(), PspLoader()]
    
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
    def __init__(self, strategies=[BarGridKernel, KdTree]):
        self.hdf5manager = HDF5Manager(strategies) 
    
    @overrides
    def read(self, filename):
        return self.hdf5manager.readKernel(filename)

import re, numpy as np

class PspLoader(FileFormatLoader):
    '''
    Reader for the output format of the software of Patrick Saint-Pierre.
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
