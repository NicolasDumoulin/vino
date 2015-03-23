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
  
  def writeData(self, data, attrs):
    self.f['data'] = data
    for key,value in attrs.iteritems():
      self.f['data'].attrs[key] = value

  def writeData(self, data, attrs, **datasets_options):
    print(datasets_options)
    self.f.create_dataset('data', data=data, **datasets_options)
    for key,value in attrs.iteritems():
      self.f['data'].attrs[key] = value
    
