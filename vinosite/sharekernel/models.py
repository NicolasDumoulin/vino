from django.db import models

# Create your models here.

class Document(models.Model):
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')

class Category(models.Model):
    text = models.CharField(max_length=200)
    color = models.IntegerField(default=0)

class ViabilityProblem(models.Model):
    category = models.ForeignKey(Category)
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


class Algorithm(models.Model):
    name = models.CharField(max_length=500,default=0)
    author = models.CharField(max_length=200,default =0)
    version = models.CharField(max_length=20,default=0)
    publication = models.TextField(max_length=1000,default =0)
    softwarewebsite = models.GenericIPAddressField(default=0)
    softwarecontact = models.EmailField(default=0)
    softwareparameters = models.CharField(max_length=500,default = 0)
    
class Parameters(models.Model):
    viabilityproblem = models.ForeignKey(ViabilityProblem)
    dynamicsparametervalues = models.CharField(max_length=200,default=0)
    stateconstraintparametervalues = models.CharField(max_length=200,default=0)
    targetparametervalues = models.CharField(max_length=200,default=0)


class ResultFormat(models.Model):
    name = models.CharField(max_length=200,default = 0)
    description = models.TextField(max_length=2000,default = 0)
    parameterlist = models.CharField(max_length=500,default = 0)
    
class Results(models.Model):
    parameters = models.ForeignKey(Parameters)
    algorithm = models.ForeignKey(Algorithm)
    resultformat = models.ForeignKey(ResultFormat,default = 0)
    title = models.CharField(max_length=200,default = 0)
    author = models.CharField(max_length=200,default = 0)
    submissiondate = models.DateTimeField('date published')
    contactemail = models.CharField(max_length=200,default = 0)
    softwareparametervalues = models.CharField(max_length=500,default = 0)
    formatparametervalues = models.CharField(max_length=500,default = 0)
    datafile = models.FileField(upload_to='results/%Y/%m/%d',default = 0)
