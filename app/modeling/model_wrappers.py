"""
Harness functions for models. VWHarness Object? Build the Python implementation
in class form and then abstract to an ontology.
"""


class ModelWrapper(object):
    """
    Model of the modeling workflow. Checks if the ModelHarness is properly
    configured before running harnessed model.
    """
    def __init__(self, arg):
        super(ModelWrapper, self).__init__()
        self.arg = arg

