from django.core.management.base import BaseCommand
from sharekernel.models import ResultFormat, ViabilityProblem, Algorithm
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
        for vp in [{
            'category':None,
            'title':'Lake eutrophication',
            'issue':'Many lake have experienced sudden shift from oligotrophic to eutrophic state. This phenomenon is due to excess phosphorus in lake. The model describes the dynamics of phosphorus concentration and the phophorus inputs.The issue is to determine wether it is possible to maintain the lake in an oligotrophic state while preserving agricultural activities in its watershed.',
            'statedimension':2,
            'statenameandabbreviation':'Phosphorus Inputs,L/Phosphorus Concentration,P',
            'controldimension':1,
            'controlnameandabbreviation':'Phosphorus Inputs Variation,u',
            'dynamicsdescription':'u,-b*P+L+r*P^q/(m^q+P^q)',
            'admissiblecontroldescription':'u>=unin,u<=unax',
            'dynamicsparameters':'b,r,q,m,unin,unax',
            'stateconstraintdescription':'L>=Lmin,L<=Lmax,P>=0,P<=Pmax',
            'stateconstraintparameters':'Lmin,Lmax,Pmax'
        },{
            'category':None,
            'title':'Language competition',
            'issue':'Many languages might become extinct. It is, therefore, an important challenge to understand language dynamics, and to recognise whether there are measures that can help us preserve some of them.',
            'statedimension':3,
            'statenameandabbreviation':'Proportion of speakers of language A,a/Proportion of speakers of language B,b/Relative prestige,s',
            'controldimension':1,
            'controlnameandabbreviation':'Prestige Variation,u',
            'dynamicsdescription':"x'=(1-x-y)(1-y)^c*z-xy^c*(1-z),y'=(1-x-y)(1-x)^c*(1-z)-yx^c*z,z'=u",
            'admissiblecontroldescription':'u in [umin;umax]',
            'dynamicsparameters':'c,umin,umax',
            'stateconstraintdescription':'x in [amin; 1],y in [bmin;1],z in [0;1],x+y in [0;1]',
            'stateconstraintparameters':'amin,bmin',
        },{
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
        
        for software in [{
            'name':'Patrick Saint-Pierre Software',
            'author':'Patrick Saint-Pierre',
            'publication':'Saint-Pierre (1994) Approximation of the viability kernel. Applied Mathematics and Optimization, 29, 187-209'
            
        },{
            'name':'Kd-Tree Software',
            'author':'Isabelle Alvarez and Romain Reuillon',
            'softwareparameters':'Exploration domain, control step, maximal division deepness, dilatation parameter, Runge-Kutta integration step, Runge-Kutta time step, random seed'
        }]:
            o = Algorithm(**software)
            try:
                o.full_clean()
            except ValidationError as e:
                self.stdout.write("Software '{}' can't be added because of these field's errors: {}".format(software['name'],e))
            o.save()
