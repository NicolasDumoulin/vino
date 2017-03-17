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

def addKernel(kernel, file):
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
    def handle(self, *args, **options):
        ResultFormat.objects.all().delete()
        ViabilityProblem.objects.all().delete()
        Algorithm.objects.all().delete()
        Parameters.objects.all().delete()
        Results.objects.all().delete()
        # Now populating some kernels
        loader = Loader()
        myre = re.compile('^#(.*):(.*)$')
        for lake in ['2D','2D_light']:
            metadata = {}
            with open('../samples/lake/'+lake+'_metadata.txt') as f:
                for line in f:
                    if line.startswith('#'):
                        k, v = myre.match(line).groups()
                        metadata[k.strip()] = v.strip()
            f = '../samples/lake/'+lake+'.txt'
            kernel = loader.load(f)
            kernel.metadata.update(metadata)
            addKernel(kernel, f)
        
        for f in ['../samples/lake/lake_Isa_R1.dat', '../samples/bilingual-viabilitree/Bilingual21TS05dil3.dat', '../samples/bilingual-viabilitree/bilingual21dil0control0.1ustep0.01WC.dat']:
            kernel = loader.load(f)
            addKernel(kernel, f)
        
        for vp in [{
            'category':None,
            'title':'Rangeland management',
            'issue':'We consider the issue of rangeland management and use a model to describe grass dynamics consisting of two parts, the crown and the shoots. We associate the grazing pressure with rangeland management policies by adjusting stock rate. However, pastoralists can not adjust stocking rates instantaneously. The aim is to design effective policies for delivering economically and environmentally viable agricultural systems.',
            'statedimension':3,
            'statenameandabbreviation':'Crown biomass,c/Shoot biomass,s/Grazing pressure,g',
            'controldimension':1,
            'controlnameandabbreviation':'Variation of grazing pressure,u',
            'dynamicsdescription':"c'=rs*s-c,s'=(a*c + rc*c*s)(1-s)-g*s,g'=u",
            'admissiblecontroldescription':'u in [umin;umax]',
            'dynamicsparameters':'rs,a,rc,umin,umax',
            'stateconstraintdescription':'c in [0;rs],s in [smin;1],g in [gmin;1]',
            'stateconstraintparameters':'smin,gmin',
        }]:
            o = ViabilityProblem(**vp)
            try:
                o.full_clean()
            except ValidationError as e:
                self.stdout.write("Viability problem '{}' can't be added because of these field's errors: {}".format(vp['title'],e))
            o.save()
            
