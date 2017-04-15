# -*- coding: utf-8 -*-

import abc
import METADATA

class Kernel(object):
  def __init__(self, metadata={}):
    self.__metadata = metadata    
  
  @property
  def metadata(self):
    return self.__metadata

  def getMetadata(self):
    return self.__metadata

  def getStateDimension(self):
    return self.metadata[METADATA.statedimension]

  @abc.abstractmethod
  def getData(self):
    '''
    Return the object representing the data of the kernel
    '''
    
  def getDataAttributes(self):
    return {
        METADATA.resultformat_title : self.getFormatCode()
          }
  
  @staticmethod   
  @abc.abstractmethod
  def getFormatCode():
    '''
    Return a string that identifies of the format.
    This identifier is used to code the format used in the metadata of the hdf5 file.
    '''
    pass
  
  @abc.abstractmethod
  def toBarGridKernel(self, newOriginCoords, newOppositeCoords, newIntervalNumberperaxis):
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
