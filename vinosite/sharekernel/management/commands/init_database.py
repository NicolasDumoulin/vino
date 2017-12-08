from django.core.management.base import BaseCommand
from sharekernel.models import *
from django.core.files import File
from FileFormatLoader import Loader
import re
import METADATA
from django.utils import timezone
from hdf5common import HDF5Manager
import tempfile
from BarGridKernel import BarGridKernel
from django.utils.text import slugify
from sharekernel.views import findandsaveobject
from django.contrib.auth.models import User

class Command(BaseCommand):
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--sure-delete',
            action='store_true',
            dest='sure-delete',
            default=False,
            help='Confirm deletion of all objects and users',
        )

    def handle(self, *args, **options):
        if not options['sure-delete']:
            self.stdout.write('''You want to delete all objects and users before
            populating the database with samples. If you know what you are doing,
            please add the argument 'sure' in the command:\n    python manage.py
            init_database --delete --sure-delete''')
            return
        ResultFormat.objects.all().delete()
        ViabilityProblem.objects.all().delete()
        Software.objects.all().delete()
        Parameters.objects.all().delete()
        Results.objects.all().delete()
        Document.objects.all().delete()
        StateVariable.objects.all().delete()
        ControlVariable.objects.all().delete()
        DynamicsParameter.objects.all().delete()
        StateConstraintParameter.objects.all().delete()
        TargetParameter.objects.all().delete()
        # Adding default users
        for username, email in [
                ['nicolas.dumoulin','nicolas.dumoulin@irstea.fr'],
                ['sophie.martin','sophie.martin@irstea.fr']
            ]:
            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(username=username, email=email, password=None)
        for title,description,params in [['bars','''Each file line contains a given number of integers ranging from 0
        to PointNumberPerAxis corresponding to a segment. The result is the union of all these segments.
        If (4,6,46,57) is written on a line, that means that the problem is 3-dimensional and that points
        (4,6,46), (4,6,47), ... ,(4,6,57) belong to the result set. Moreover, all real-valued points whose
        sup-distance is smaller than PointSize/2 also belong to the result set. ColumnDescription corresponds
        to identity matrix if the file columns correspond to the order according to which variables appear in
        the model description. Again in dimension 3 for instance, (0,0,0) corresponds to MinimalValues
        (possibly interchanged according to ColumnDescription) and (PointNumberPerAxis,PointNumberPerAxis,
        PointNumberPerAxis) to MaximalValues.''',
        'MinimalValues,MaximalValues,PointNumberPerAxis,PointSize,ColumnDescription'],
        ['kdtree','''Each file line contains a given number of real numbers separated by a blank describing
        the coordinates of one point in the cube, then the minimum and maximum values on each axis describing
        the cube belonging to the approximated kernel.''','statedimension;ColumnDescription']]:
            ResultFormat(title=title, description=description, parameterlist=params).save()
