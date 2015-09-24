# -*- coding: utf8 -*-

import h5py

class HDF5Writer:
  def __init__(self, filename):
    self.f = h5py.File(filename, 'w')
    self.metadata = self.f.create_group('metadata')

  def __enter__(self):
    return self
      
  def __exit__(self, type, value, traceback):
    self.f.close()

  def writeMetadata(self, metadata):
    '''
    Write metadata. TODO need to be specified.
    Maybe we need 2 categories:
     - viability problem and its dynamics parameters
     - kernel approximation algorithm and its parameters
    '''
    self.metadata = metadata
  
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

class HDF5Manager:
  def __init__(self, strategies):
    self.formatsStrategies = { s.getFormatCode():s for s in strategies }

  def readKernel(self, filename):
    '''
    Read a kernel from a Vino HDF5 file and returns a subclass of the class
    Kernel depending of the detected storage format.
    '''
    with HDF5Reader(filename) as f:
      # TODO nothing is done with these metadata
      metadata = f.readMetadata()
      # reading the data attributes for determining the format
      dataAttributes = f.readDataAttributes()
      return self.formatsStrategies[dataAttributes['format']].initFromHDF5(metadata, dataAttributes, f.readData())

  @staticmethod
  def writeKernel(kernel, filename, **datasets_options):
    '''
    Write a kernel to a Vino HDF5 file
    '''
    with HDF5Writer(filename) as w:
      w.writeMetadata(kernel.getMetadata())
      w.writeData(kernel.getData(), kernel.getDataAttributes(), **datasets_options)   
  
    