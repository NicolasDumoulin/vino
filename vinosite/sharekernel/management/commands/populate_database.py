from django.core.management.base import BaseCommand
from sharekernel.models import ResultFormat
from django.core.exceptions import ValidationError

class Command(BaseCommand):
    def handle(self, *args, **options):
        for name, description, parameterlist in [
            ['bars','Each file line contains a given number of integers ranging from 0 to PointNumberPerAxis corresponding to a segment. The result is the union of all these segments. If (4,6,46,57) is written on a line, that means that the problem is 3-dimensional and that points (4,6,46), (4,6,47), ... ,(4,6,57) belong to the result set. Moreover, all real-valued points whose sup-distance is smaller than PointSize/2 also belong to the result set. ColumnDescription corresponds to identity matrix if the file columns correspond to the order according to which variables appear in the model description. Again in dimension 3 for instance, (0,0,0) corresponds to MinimalValues (possibly interchanged according to ColumnDescription) and (PointNumberPerAxis,PointNumberPerAxis,PointNumberPerAxis) to MaximalValues.','MinimalValues,MaximalValues,PointNumberPerAxis,PointSize,ColumnDescription'],
            ['kdtree','Each file line contains a given number of real numbers separated by a blank describing the coordinates of one point in the cube, then the minimum and maximum values on each axis describing the cube belonging to the approximated kernel.','ColumnDescription']
            ]:
            o = ResultFormat(name=name, description=description, parameterlist=parameterlist)
            try:
                o.full_clean()
            except ValidationError as e:
                self.stdout.write("Format '{}' can't be added because of these field's errors: {}".format(name,e))
            o.save()
