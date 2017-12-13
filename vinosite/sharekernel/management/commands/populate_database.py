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
from init_database import clear_database, create_defaultusers, create_defaultformats

hdf5manager = HDF5Manager([BarGridKernel])

def addKernel(kernel, user):
    resultformat_md = {k:v for k,v in kernel.metadata.iteritems() if k.startswith("resultformat")}
    resultformat = findandsaveobject(ResultFormat,
        metadata={METADATA.resultformat_title:resultformat_md[METADATA.resultformat_title]},
        fields={'submitter':user}, add_metadata=resultformat_md)
    problem_md = {k:v for k,v in kernel.metadata.iteritems() if k.startswith("viabilityproblem")}
    relatedforeignkeys={}
    for varType in [StateVariable, ControlVariable, DynamicsParameter, StateConstraintParameter, TargetParameter]:
        metadatakey = getattr(METADATA, varType.__name__.lower()+"s")
        variables=[]
        relatedforeignkeys[varType] = variables
        for v in eval(problem_md[metadatakey]):
            # put default values to ensure to have 3 elements
            v = v + [""]*(3-len(v))
            variables.append(varType(shortname=v[0], name=v[1], unit=v[2]))
        del problem_md[metadatakey]
    problem = findandsaveobject(ViabilityProblem,
        metadata=problem_md,
        relatedforeignkeys=relatedforeignkeys,
        fields={'submitter':user}, add_metadata=problem_md)
    parameters_md = {k:v for k,v in kernel.metadata.iteritems() if k.startswith("parameters")}
    parameters = findandsaveobject(Parameters, parameters_md,
        foreignkeys={'viabilityproblem':problem}, fields={'submitter':user})
    software_md = {k:v for k,v in kernel.metadata.iteritems() if k.startswith("software")}
    software = findandsaveobject(Software,
        metadata={METADATA.software_title:software_md[METADATA.software_title]},
        fields={'submitter':user}, add_metadata=software_md)
    # obtaining an unique filename
    tmpfile = tempfile.NamedTemporaryFile(prefix=slugify(kernel.metadata[METADATA.title]),suffix=".h5")
    filename = tmpfile.name
    tmpfile.close()
    hdf5manager.writeKernel(kernel, filename)
    result = findandsaveobject(Results, kernel.metadata, foreignkeys={
            "parameters": parameters,
            "software": software,
            "resultformat": resultformat
        },fields={
            "datafile": File(open(filename), name=filename),
            "submissiondate": timezone.now(),
            'submitter':user
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
            help='Delete all objects and users',
        )
        parser.add_argument(
            '--sure-delete',
            action='store_true',
            dest='sure-delete',
            default=False,
            help='Confirm deletion of all objects and users',
        )

    def handle(self, *args, **options):
        if options['delete']:
            if not options['sure-delete']:
                self.stdout.write("You want to delete all objects and users before populating the database with samples. If you know what you are doing, please add the argument 'sure' in the command:\n    python manage.py populate_database --delete --sure-delete")
                return
            clear_database()
            create_defaultformats()
        # Adding default users
        create_defaultusers()
        user = User.objects.first()
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
            print(f)
            kernel = loader.load(f)
            kernel.metadata.update(metadata)
            addKernel(kernel, user)

        for f in ['../samples/lake/lake_Isa_R1.dat', '../samples/bilingual-viabilitree/Bilingual21TS05dil3.dat', '../samples/bilingual-viabilitree/bilingual21dil0control0.1ustep0.01WC.dat']:
            print(f)
            kernel = loader.load(f)
            addKernel(kernel, user)
