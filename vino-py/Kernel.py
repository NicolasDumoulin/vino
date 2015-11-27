# -*- coding: utf-8 -*-

import abc

class Kernel(object):
  def __init__(self, metadata={}):
    self.metadata = metadata    
    
  def getMetadata(self):
    return self.metadata

  @abc.abstractmethod
  def getData(self):
    '''
    Return the object representing the data of the kernel
    '''
    
  def getDataAttributes(self):
    return {
        'format' : self.getFormatCode()
          }
  
  @staticmethod   
  @abc.abstractmethod
  def getFormatCode():
    '''
    Return a string that identifies of the format.
    This identifier is used to code the format used in the metadata of the hdf5 file.
    '''
    pass
  
  @classmethod
  @abc.abstractmethod
  def initFromHDF5(cls, metadata, dataAttributes, hdf5data):
    '''
    Init a kernel from Vino HDF5 data.
    '''
  
  @abc.abstractmethod
  def isInSet(self, point):
    '''
    Return a boolean to indicate if a point is inside or outside from this kernel.
    '''
