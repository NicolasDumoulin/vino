from django.core.management.base import BaseCommand
from sharekernel.models import ResultFormat, Parameters, ViabilityProblem, Algorithm, Results
from django.core.files import File
from django.core.exceptions import ValidationError
from FileFormatLoader import Loader
import re
import METADATA
from django.utils import timezone
from hdf5common import HDF5Manager
import tempfile
from BarGridKernel import BarGridKernel
from django.utils.text import slugify
from sharekernel.views import findandsaveobject

hdf5manager = HDF5Manager([BarGridKernel])

def addKernel(kernel):
    resultformat_md = {k:v for k,v in kernel.metadata.iteritems() if k.startswith("resultformat")}
    resultformat = findandsaveobject(ResultFormat, {METADATA.resultformat_name:resultformat_md[METADATA.resultformat_name]}, add_metadata=resultformat_md)
    problem_md = {k:v for k,v in kernel.metadata.iteritems() if k.startswith("viabilityproblem")}
    problem = findandsaveobject(ViabilityProblem, {METADATA.title:problem_md[METADATA.title]}, add_metadata=problem_md)
    parameters_md = {k:v for k,v in kernel.metadata.iteritems() if k.startswith("parameters")}
    parameters = findandsaveobject(Parameters, parameters_md, foreignkeys={'viabilityproblem':problem})
    algorithm_md = {k:v for k,v in kernel.metadata.iteritems() if k.startswith("algorithm")}
    algorithm = findandsaveobject(Algorithm, {METADATA.algorithm_name:algorithm_md[METADATA.algorithm_name]}, add_metadata=algorithm_md)
    tmpfile = tempfile.NamedTemporaryFile(prefix=slugify(kernel.metadata[METADATA.title]),suffix=".h5")
    hdf5manager.writeKernel(kernel, tmpfile.name)
    result = findandsaveobject(Results, kernel.metadata, foreignkeys={
            "parameters": parameters,
            "algorithm": algorithm,
            "resultformat": resultformat
        },fields={
            "datafile": File(tmpfile),
            "submissiondate": timezone.now()
    })
    return result

class Command(BaseCommand):
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--delete',
            action='store_true',
            dest='delete',
            default=False,
            help='Delete all objects',
        )
        parser.add_argument(
            '--sure-delete',
            action='store_true',
            dest='sure-delete',
            default=False,
            help='Confirm deletion of all objects',
        )

    def handle(self, *args, **options):
        if options['delete']:
            if not options['sure-delete']:
                self.stdout.write("You want to delete all objects before populating the database with samples. If you know what you are doing, please add the argument 'sure' in the command:\n    python manage.py populate_database --delete --sure-delete")
                return
            ResultFormat.objects.all().delete()
            ViabilityProblem.objects.all().delete()
            Algorithm.objects.all().delete()
            Parameters.objects.all().delete()
            Results.objects.all().delete()
        # Now populating some kernels
        loader = Loader()
        myre = re.compile('^#(.*):(.*)$')
        for prefix in ['lake/2D','lake/2D_light','rangeland/3D_rangeland']:
            metadata = {}
            with open('../samples/'+prefix+'_metadata.txt') as f:
                for line in f:
                    if line.startswith('#'):
                        k, v = myre.match(line).groups()
                        metadata[k.strip()] = v.strip()
            f = '../samples/'+prefix+'.txt'
            kernel = loader.load(f)
            kernel.metadata.update(metadata)
            addKernel(kernel)
        
        for f in ['../samples/lake/lake_Isa_R1.dat', '../samples/bilingual-viabilitree/Bilingual21TS05dil3.dat', '../samples/bilingual-viabilitree/bilingual21dil0control0.1ustep0.01WC.dat']:
            kernel = loader.load(f)
            addKernel(kernel)

            
