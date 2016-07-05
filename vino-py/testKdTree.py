from KdTree import *
import METADATA
import unittest2 as unittest

class TestKdTree(unittest.TestCase):
    def test_toBarGridKernel(self):
        cells = [[0,0,0]+p for p in [[1,2,4,5,8,9],[2,3,4,5,8,9],[2,3,5,6,8,9],[2,3,4,5,7,8],[2,3,5,6,4,5]]]
        kdt = KdTree(cells = cells, metadata={ METADATA.statedimension: 3 })
        bgk = kdt.toBarGridKernel(intervalsSizes = [1,1,1], newOriginCoords = [1,4,4], newOppositeCoords = [3,6,9])
        self.assertEqual(len(bgk.bars), 12)
        bgk = kdt.toBarGridKernel([1,1,1])
        self.assertEqual(len(bgk.bars), 4)
        
    def test_isInSet(self):
        cells = [[0,0,0]+p for p in [[1,2,4,5,8,9],[2,3,4,5,8,9],[2,3,5,6,8,9],[2,3,4,5,6,7]]]
        kdt = KdTree(cells = cells, metadata={ METADATA.statedimension: 3})
        for inSetPoint in [[1, 4, 8], [2.5,4.5,9], [2.5,4.5,8], [2.5,4.5,6]]:
            self.assertTrue(kdt.isInSet(inSetPoint), inSetPoint)
        for outSetPoint in [[3.1, 4, 8], [1, 4, 9.2], [2.5,4.5,7.5], [2.5,4.5,3]]:
            self.assertFalse(kdt.isInSet(outSetPoint), outSetPoint)
        
  
if __name__ == '__main__':
    import xmlrunner
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))
    
