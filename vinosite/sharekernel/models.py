from django.db import models
from django.conf import settings
from Equation import Expression
from django.utils import timezone

class BaseEntity(models.Model):
    title = models.CharField(max_length=500,default='')
    description = models.TextField(max_length=2000,default = '', blank=True)
    publication = models.TextField(max_length=1000,default ='', blank=True)
    website = models.URLField(default='', blank=True)
    submissiondate = models.DateTimeField('date published', default=timezone.now)
    submitter = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
    author = models.CharField(max_length=500,default='', blank=True)
    contact = models.CharField(max_length=500,default='', blank=True)
    illustration = models.ImageField(upload_to='illustrations', default=None, blank=True)

    class Meta:
        abstract = True

class Document(models.Model):
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')

class ViabilityProblem(BaseEntity):
    dynamicsdescription = models.CharField(max_length=500,default =0)
    admissiblecontroldescription = models.CharField(max_length=500,default =0)
    stateconstraintdescription = models.CharField(max_length=500,default =0)
    targetdescription = models.CharField(max_length=500,default =0)
    def dynamics(self):
      return [fulldyn.split("=")[1] for fulldyn in self.dynamicsdescription.split(",")]
    def constraints(self):
      return self.stateconstraintdescription.split(",")
    def admissibles(self):
      return self.admissiblecontroldescription.split(",")
    def stateabbreviation(self):
      return [v.shortname for v in self.statevariables.all()]
    def statename(self):
      return [v.name for v in self.statevariables.all()]
    def controlabbreviation(self):
      return [v.shortname for v in self.controlvariables.all()]
    def controlname(self):
      return [v.name for v in self.controlvariables.all()]
    def stateconstraintparameterabbreviation(self):
      return [v.shortname for v in self.stateconstraintparameters.all()]


    def __str__(self):
        return str(self.pk) + " " + self.title

class Variable(models.Model):
    shortname = models.CharField(max_length=500)
    name = models.CharField(max_length=500,default ='', blank=True)
    unit = models.CharField(max_length=500,default ='', blank=True)
    class Meta:
        abstract = True
    def __repr__(self):
        return '["{}","{}","{}"]'.format(self.shortname, self.name, self.unit)
    def testrepr(self):
        return '["{}","{}","{}"]'.format(shortname, name, unit)
    def __str__(self):
        name = ""
        if len(self.name) > 1:
            name = " (" + self.name+")"
        return str(self.shortname) + name

class StateVariable(Variable):
    viabilityproblem = models.ForeignKey(ViabilityProblem, related_name='statevariables', on_delete=models.CASCADE)

class ControlVariable(Variable):
    viabilityproblem = models.ForeignKey(ViabilityProblem, related_name='controlvariables', on_delete=models.CASCADE)

class DynamicsParameter(Variable):
    viabilityproblem = models.ForeignKey(ViabilityProblem, related_name='dynamicsparameters', on_delete=models.CASCADE)

class StateConstraintParameter(Variable):
    viabilityproblem = models.ForeignKey(ViabilityProblem, related_name='stateconstraintparameters', on_delete=models.CASCADE)

class TargetParameter(Variable):
    viabilityproblem = models.ForeignKey(ViabilityProblem, related_name='targetparameters', on_delete=models.CASCADE)

class Software(BaseEntity):
    version = models.CharField(max_length=20,default='', blank=True)
    parameters = models.CharField(max_length=500,default = '', blank=True)
    def __str__(self):
        return str(self.pk) + " " + self.title + " " + self.version

class Parameters(BaseEntity):
    viabilityproblem = models.ForeignKey(ViabilityProblem)
    dynamicsparametervalues = models.CharField(max_length=200,default='', blank=True)
    stateconstraintparametervalues = models.CharField(max_length=200,default='', blank=True)
    targetparametervalues = models.CharField(max_length=200,default='', blank=True)
    def speed(self):
        eqdyns = []
        desstateandcontrol = []
        desdyn = self.viabilityproblem.dynamics()
        j=0
        for thing in self.viabilityproblem.dynamicsparameters.all():
             for i in range(len(desdyn)):
                  desdyn[i] = desdyn[i].replace(thing.shortname,self.dynamicsparametervalues.split(",")[j])
             j = j+1
        params= self.viabilityproblem.stateabbreviation()+self.viabilityproblem.controlabbreviation()

        for expr in desdyn :
            eqdyns.append(Expression(expr,params))
        return eqdyns
    def __str__(self):
        return str(self.pk) + " " + self.dynamicsparametervalues

    def admissibles(self):
        eqadms = []
        desstateandcontrol = []
        desadm = self.viabilityproblem.admissibles()
        j=0
        for thing in self.viabilityproblem.dynamicsparameters.all():
             for i in range(len(desadm)):
                  desadm[i] = desadm[i].replace(thing.shortname,self.dynamicsparametervalues.split(",")[j])
             j = j+1
        params= self.viabilityproblem.stateabbreviation()+self.viabilityproblem.controlabbreviation()

        for expr in desadm :
            eqadms.append(Expression(expr,params))
        return eqadms

    def constraints(self):
        eqcons = []
        desstateandcontrol = []
        descon = self.viabilityproblem.constraints()
        j=0
#        for thing in self.viabilityproblem.stateconstraintparameters.split(","):
        for thing in self.viabilityproblem.stateconstraintparameterabbreviation():
             for i in range(len(descon)):
                  descon[i] = descon[i].replace(thing,self.stateconstraintparametervalues.split(",")[j])
             j = j+1
        params= self.viabilityproblem.stateabbreviation()

        for expr in descon :
            eqcons.append(Expression(expr,params))
        return eqcons


    def leftandrighthandconstraints(self):
        eqcons = []
        desstateandcontrol = []
        descon = self.viabilityproblem.constraints()
        j=0
        for thing in self.viabilityproblem.stateconstraintparameterabbreviation():
             for i in range(len(descon)):
                  descon[i] = descon[i].replace(thing,self.stateconstraintparametervalues.split(",")[j])
             j = j+1
        params= self.viabilityproblem.stateabbreviation()

        for i in range(len(descon)):
             desconsplitted = descon[i].split("<=");
             if (len(desconsplitted)==2):
                 eqcons.append([Expression(desconsplitted[0],params),Expression(desconsplitted[1],params)])
             else :
                 desconsplitted = descon[i].split(">=");
                 if (len(desconsplitted)==2):
                     eqcons.append([Expression(desconsplitted[1],params),Expression(desconsplitted[0],params)])
        return eqcons

class ResultFormat(BaseEntity):
    parameterlist = models.CharField(max_length=500,default = '', blank=True)

    def __str__(self):
        return self.title

    def toDict(self):
        '''
        Return a representation of the format as a dictionnary.
        '''
        return {"pk":self.pk, "format":self.title, "description":self.description, "parameters":self.parameterlist.split(";")}

class Results(BaseEntity):
    parameters = models.ForeignKey(Parameters, null = True)
    software = models.ForeignKey(Software, null = True)
    resultformat = models.ForeignKey(ResultFormat, null=True)
    softwareparametervalues = models.CharField(max_length=500,default = '', blank=True)
    formatparametervalues = models.CharField(max_length=500,default = '', blank=True)
    datafile = models.FileField(upload_to='results/%Y/%m/%d')
    def __str__(self):
        return str(self.pk) + " " + str(self.submissiondate.strftime("%Y%m%d-%H%M"))+ " " + self.title

class StateSet(BaseEntity):
    '''
    Representation of a set of system states, independent of any dynamics or viability problem.
    This intends to be used for:
     - storing the result of an operation between two "Results" (for example a difference)
     - describing a complex constraint set of viability problem
    '''
    resultformat = models.ForeignKey(ResultFormat, null=True)
    datafile = models.FileField(upload_to='statesets/%Y/%m/%d')
    parents = models.ManyToManyField(Results, default=None)
