from abc import ABCMeta, abstractmethod


"""
These abstract classes are used to implement dependency inversion. 
"""


# aka use case or interactor
class IInputBoundary(metaclass=ABCMeta):

    @abstractmethod
    def execute(self, request_model, output_port):
        """
        :param request_model: should be dump input DTO (may be namedtuple) from entities layer
        :param output_port: should be presenter or suchlike as subclass of IOutputBoundary
        """
        pass


# aka presenter or something like this
class IOutputBoundary(metaclass=ABCMeta):

    @abstractmethod
    def present(self, response_model):
        """
        :param response_model: should be dump output DTO (may be namedtuple) from entities layer
        """
        pass
