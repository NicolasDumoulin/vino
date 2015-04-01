# -*- coding: utf8 -*-

import numpy as np
import h5py

class HDF5Writer:
  def __init__(self, filename):
    self.f = h5py.File(filename, 'w')
    self.metadata = self.f.create_group('metadata')

  def __enter__(self):
    return self
      
  def __exit__(self, type, value, traceback):
    self.f.close()

  def writeMetadata(self, problem, algorithm):
    self.metadata['problem']=problem
    self.metadata['algorithm']=algorithm
  
  def writeData(self, data, attrs, **datasets_options):
    '''
    Writes data and their attributes (metadata on the format, boundaries, …). Options can also be passed to the writer for enabling a compression method.
    '''
    self.f.create_dataset('data', data=data, **datasets_options)
    for key,value in attrs.iteritems():
      self.f['data'].attrs[key] = value

class HDF5Reader:    
  def __init__(self, filename):
    self.f = h5py.File(filename, 'r')

  def __enter__(self):
    return self
      
  def __exit__(self, type, value, traceback):
    self.f.close()

  def readMetadata(self):
    return {key:value.value for key,value in self.f['metadata'].iteritems()}

  def readData(self):
    return self.f['data'].value

  def readDataAttributes(self):
    return {key:value for key,value in self.f['data'].attrs.items()}

import BarGridKernel
formatsStrategies = { 'bars': BarGridKernel.BarGridKernel }

def readKernel(filename):
  ''' Read a kernel from a Vino HDF5 file, using the appropriate stored format. '''
  with HDF5Reader(filename) as f:
    # TODO nothing is done with these metadata
    metadata = f.readMetadata()
    # reading the data attributes for determining the format
    dataAttributes = f.readDataAttributes()
    return formatsStrategies[dataAttributes['format']].initFromHDF5(dataAttributes, f.readData())

    