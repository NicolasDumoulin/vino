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
    author = models.CharField(max_length=500,default='')
    contact = models.CharField(max_length=500,default='')
    illustration = models.ImageField(upload_to='illustrations', default=None, blank=True)

    class Meta:
        abstract = True

class Document(models.Model):
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')

class ViabilityProblem(BaseEntity):
    statedimension = models.IntegerField(default=0)
    statenameandabbreviation = models.CharField(max_length=500,default =0)
    controldimension = models.IntegerField(default =0)
    controlnameandabbreviation = models.CharField(max_length=500,default =0)
    dynamicsdescription = models.CharField(max_length=500,default =0)
    admissiblecontroldescription = models.CharField(max_length=500,default =0)
    dynamicsparameters = models.CharField(max_length=200,default =0)
    stateconstraintdescription = models.CharField(max_length=500,default =0)
    stateconstraintparameters = models.CharField(max_length=500,default =0)
    targetdescription = models.CharField(max_length=500,default =0)
    targetparameters = models.CharField(max_length=500,default =0)
    def dynamics(self):
      dyns = []
      for fulldyn in self.dynamicsdescription.split(","):
          dyns.append(fulldyn.split("=")[1])
      return dyns

    def constraints(self):
      dyns = self.stateconstraintdescription.split(",")
      return dyns

    def admissibles(self):
      dyns = self.admissiblecontroldescription.split(",")
      return dyns

    def stateabbreviation(self):
      abbrevs = []
      donnees = self.statenameandabbreviation.split("/")
      for d in donnees:
          abbrevs.append((d.split(",")[1]))
      return abbrevs
    def statename(self):
      names = []
      donnees = self.statenameandabbreviation.split("/")
      for d in donnees:
          names.append(d.split(",")[0])
      return names
    def controlabbreviation(self):
      abbrevs = []
      donnees = self.controlnameandabbreviation.split("/")
      for d in donnees:
          abbrevs.append(d.split(",")[1])
      return abbrevs
    def controlname(self):
      names = []
      donnees = self.controlnameandabbreviation.split("/")
      for d in donnees:
          names.append(d.split(",")[0])
      return names

    def __str__(self):
        return str(self.pk) + " " + self.title

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
        for thing in self.viabilityproblem.dynamicsparameters.split(","):
             for i in range(len(desdyn)):
                  desdyn[i] = desdyn[i].replace(thing,self.dynamicsparametervalues.split(",")[j])
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
        for thing in self.viabilityproblem.dynamicsparameters.split(","):
             for i in range(len(desadm)):
                  desadm[i] = desadm[i].replace(thing,self.dynamicsparametervalues.split(",")[j])
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
        for thing in self.viabilityproblem.stateconstraintparameters.split(","):
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
        for thing in self.viabilityproblem.stateconstraintparameters.split(","):
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
