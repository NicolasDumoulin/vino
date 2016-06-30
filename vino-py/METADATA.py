class _constants:
    class ConstError(TypeError): pass

    def __setattr__(self, name, value):
        if self.__dict__.has_key(name):
            raise self.ConstError, "Can't rebind const( % s)" % name
        self.__dict__[name] = value

    def __delattr__(self, name):
        if self.__dict__.has_key(name):
            raise self.ConstError, "Can't unbind const(%s)" % name
        raise NameError, name
        
import sys
constants = _constants()

constants.category = 'category.text'
constants.title = 'viabilityproblem.title'
constants.issue = 'viabilityproblem.issue'
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
constants.algorithm_name = 'algorithm.name'
constants.algorithm_author = 'algorithm.author'
constants.algorithm_version = 'algorithm.version'
constants.algorithm_publication = 'algorithm.publication'
constants.algorithm_softwarewebsite = 'algorithm.softwarewebsite'
constants.algorithm_softwarecontact = 'algorithm.softwarecontact'
constants.algorithm_softwareparameters = 'algorithm.softwareparameters'
constants.parameters_dynamicsparametervalues = 'parameters_dynamicsparametervalues'
constants.parameters_stateconstraintparametervalues = 'parameters.stateconstraintparametervalues'
constants.parameters_targetparametervalues = 'parameters.targetparametervalues'
constants.resultformat_name = 'resultformat.name'
constants.resultformat_description = 'resultformat.description'
constants.resultformat_parameterlist = 'resultformat.parameterlist'
constants.results_title = 'results.title'
constants.results_author = 'results.author'
constants.results_submissiondate = 'results.submissiondate'
constants.results_contactemail = 'results.contactemail'
constants.results_softwareparametervalues = 'results.softwareparametervalues'
constants.results_formatparametervalues = 'results.formatparametervalues'

sys.modules[__name__] = constants

def gen_list(cls):
    '''
    Utility function for printing constants from Class definition (especially Django data model)
    '''
    for f in filter(lambda f:not f.primary_key and not f.is_relation, cls._meta.fields):
        print 'constants.' + cls.__name__.lower() + '.' + f.name + " = '" + cls.__name__.lower() + '.' + f.name + "'"
        
