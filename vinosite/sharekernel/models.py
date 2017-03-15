from django.db import models
from Equation import Expression

# Create your models here.

class Document(models.Model):
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')

class Category(models.Model):
    text = models.CharField(max_length=200)
    color = models.IntegerField(default=0)
    def __str__(self):
        return str(self.pk) + " " + self.text

class ViabilityProblem(models.Model):
    category = models.ForeignKey(Category, null = True)
    title = models.CharField(max_length=200)
    issue = models.TextField(max_length=2000,default =0)
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
      dyns = self.dynamicsdescription.split(",")
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


class Algorithm(models.Model):
    name = models.CharField(max_length=500,default=0)
    author = models.CharField(max_length=200,default =0)
    version = models.CharField(max_length=20,default=0)
    publication = models.TextField(max_length=1000,default =0)
    softwarewebsite = models.URLField(default=0)
    softwarecontact = models.EmailField(default=0)
    softwareparameters = models.CharField(max_length=500,default = 0)
    def __str__(self):
        return str(self.pk) + " " + self.name + " " + self.version
    
class Parameters(models.Model):
    viabilityproblem = models.ForeignKey(ViabilityProblem)
    dynamicsparametervalues = models.CharField(max_length=200,default=0)
    stateconstraintparametervalues = models.CharField(max_length=200,default=0)
    targetparametervalues = models.CharField(max_length=200,default=0)
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

class ResultFormat(models.Model):
    name = models.CharField(primary_key=True, max_length=200,default = 0)
    description = models.TextField(max_length=2000,default = 0)
    parameterlist = models.CharField(max_length=500,default = 0)
    
    def __str__(self):
        return str(self.pk) + " " + self.name
    
    def toDict(self):
        '''
        Return a representation of the format as a dictionnary.
        '''
        return {"pk":self.pk, "format":self.name, "description":self.description, "parameters":self.parameterlist.split()}
            
    
class Results(models.Model):
    parameters = models.ForeignKey(Parameters, null = True)
    algorithm = models.ForeignKey(Algorithm, null = True)
    resultformat = models.ForeignKey(ResultFormat,default = 0)
    title = models.CharField(max_length=200,default = 0)
    author = models.CharField(max_length=200,default = 0)
    submissiondate = models.DateTimeField('date published')
    contactemail = models.CharField(max_length=200,default = 0)
    softwareparametervalues = models.CharField(max_length=500,default = 0)
    formatparametervalues = models.CharField(max_length=500,default = 0)
    datafile = models.FileField(upload_to='results/%Y/%m/%d',default = 0)
    def __str__(self):
        return str(self.pk) + " " + str(self.submissiondate.strftime("%Y%m%d-%H%M"))+ " " + self.title

