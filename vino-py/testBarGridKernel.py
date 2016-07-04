from BarGridKernel import *
import unittest2 as unittest

class TestBarGridKernel(unittest.TestCase):
    def test_addBar(self):
        grid = BarGridKernel([0, 0, 0], [10, 10, 10], [10, 10, 10])
        grid.addBar([1, 1], 3, 5)
        grid.addBar([1, 1], 7, 9)
        grid.addBar([1, 1], 2, 8)
        self.assertEqual(len(grid.bars), 1)
        self.assertEqual(grid.bars[0], [1,1,2,9])
        grid.addBar([1, 2], 3, 4)
        grid.addBar([1, 2], 4, 6)
        self.assertEqual(len(grid.bars), 2)
        self.assertEqual(grid.bars[1], [1,2,3,6])

        grid = BarGridKernel([0, 0, 0], [10, 10, 10], [10, 10, 10])
        grid.addBar([1, 1], 3, 3)
        grid.addBar([1, 1], 4, 4)
        self.assertEqual(len(grid.bars), 1)
        self.assertEqual(grid.bars[0], [1,1,3,4])
        
        grid = BarGridKernel([0, 0, 0], [10, 10, 10], [10, 10, 10])
        grid.addBar([1, 1], 3, 5)
        grid.addBar([1, 1], 7, 9)
        grid.addBar([1, 1], 2, 9)
        self.assertEqual(len(grid.bars), 1)
        self.assertEqual(grid.bars[0], [1,1,2,9])
        
        grid = BarGridKernel([0, 0, 0], [10, 10, 10], [10, 10, 10])
        grid.addBar([1, 1], 3, 5)
        grid.addBar([1, 1], 7, 9)
        grid.addBar([1, 1], 6, 9)
        self.assertEqual(len(grid.bars), 1)
        self.assertEqual(grid.bars[0], [1,1,3,9])
        
    def test_isInSet(self):
        grid = BarGridKernel([0, 0], [10, 10], [10, 10])
        grid.addBar([1], 3, 7)
        grid.addBar([2], 5, 5)
        grid.addBar([3], 0, 10)
        for inSetPoint in [[1, 3], [0.5, 2.5], [1, 2.8], [1, 2.5], [1, 5], [1, 7], [1, 7.5], [2, 5], [3, 0], [3, 10]]:
            self.assertTrue(grid.isInSet(inSetPoint), inSetPoint)
        for outSetPoint in [[0, 5], [1, 2.4], [1, 7.6], [2, 6], [5, 5]]:
            self.assertFalse(grid.isInSet(outSetPoint), outSetPoint)
        grid = BarGridKernel([0, 0, 0], [10, 10, 10], [10, 10, 10])
        grid.addBar([1, 1], 3, 7)
        grid.addBar([1, 2], 3, 7)
        grid.addBar([2, 2], 4, 6)
        grid.addBar([2, 3], 3, 5)
        grid.addBar([2, 3], 6, 9)
        for inSetPoint in [[1, 1, 2.5],[1, 1, 7.5],[1, 0.5, 3.5],[1.5, 1.5, 7.5],[2.5, 2.5, 3]]:
            self.assertTrue(grid.isInSet(inSetPoint), inSetPoint)
        for outSetPoint in [[1, 1, 2.4],[1, 1, 7.6]]:
            self.assertFalse(grid.isInSet(outSetPoint), outSetPoint)
   
  
if __name__ == '__main__':
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))
    
    
    