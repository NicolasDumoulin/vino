import unittest

from BarGridKernel import *

class TestBarGridKernel(unittest.TestCase):
    def testIsInSet(self):
        grid = BarGridKernel([0,0], [10,10], [11,11])
        grid.addBar([1],3,7)
        grid.addBar([2],5,5)
        grid.addBar([3],0,10)
        for inSetPoint in [[1,5], [2,5], [3,0], [3,10]]:
            self.assertTrue(grid.isInSet,inSetPoint)
        for outSetPoint in [[0,5], [1,2], [2,6], [5,5]]:
            self.assertTrue(grid.isInSet,outSetPoint)
  
if __name__ == '__main__':
  import xmlrunner
  unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))
  
