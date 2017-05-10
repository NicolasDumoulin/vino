class _constants:
    class ConstError(TypeError): pass

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise self.ConstError("Can't rebind const( % s)" % name)
        self.__dict__[name] = value

    def __delattr__(self, name):
        if name in self.__dict__:
            raise self.ConstError("Can't unbind const(%s)" % name)
        raise NameError(name)
    
    def keys(self):
        return self.__dict__.keys()
               
    def values(self):
        return self.__dict__.values()
               
import sys
constants = _constants()

constants.category = 'category.text'
constants.title = 'viabilityproblem.title'
constants.description = 'viabilityproblem.description'
constants.statedimension = 'viabilityproblem.statedimension'
constants.statenameandabbreviation = 'viabilityproblem.statenameandabbreviation'
constants.controldimension = 'viabilityproblem.controldimension'
constants.controlnameandabbreviation = 'viabilityproblem.controlnameandabbreviation'
constants.dynamicsdescription = 'viabilityproblem.dynamicsdescription'
constants.admissiblecontroldescription = 'viabilityproblem.admissiblecontroldescription'
constants.dynamicsparameters = 'viabilityproblem.dynamicsparameters'
constants.stateconstraintdescription = 'viabilityproblem.stateconstraintdescription'
constants.stateconstraintparameters = 'viabilityproblem.stateconstraintparameters'
constants.targetdescription = 'viabilityproblem.targetdescription'
constants.targetparameters = 'viabilityproblem.targetparameters'
constants.software_title = 'software.title'
constants.software_author = 'software.author'
constants.software_version = 'software.version'
constants.software_publication = 'software.publication'
constants.software_website = 'software.website'
constants.software_contact = 'software.contact'
constants.software_parameters = 'software.parameters'
constants.parameters_dynamicsparametervalues = 'parameters_dynamicsparametervalues'
constants.parameters_stateconstraintparametervalues = 'parameters.stateconstraintparametervalues'
constants.parameters_targetparametervalues = 'parameters.targetparametervalues'
constants.resultformat_title = 'resultformat.title'
constants.resultformat_description = 'resultformat.description'
constants.resultformat_parameterlist = 'resultformat.parameterlist'
constants.results_title = 'results.title'
constants.results_author = 'results.author'
constants.results_submissiondate = 'results.submissiondate'
constants.results_contact = 'results.contact'
constants.results_softwareparametervalues = 'results.softwareparametervalues'
constants.results_formatparametervalues = 'results.formatparametervalues'

sys.modules[__name__] = constants

def gen_list(cls):
    '''
    Utility function for printing constants from Class definition (especially Django data model)
    '''
    for f in [f for f in cls._meta.fields if not f.primary_key and not f.is_relation]:
        print('constants.' + cls.__name__.lower() + '.' + f.name + " = '" + cls.__name__.lower() + '.' + f.name + "'")
        
