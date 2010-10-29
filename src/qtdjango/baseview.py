
# -*- coding: utf-8 -*-
class BaseView(object):
    '''
    classdocs
    '''
    fields = ()
    widgets = {}
    model = None


    exclude_fields = ("id")
    """@cvar: Tuple of fields that must exclude from view"""

    def __init__(self, **kwargs):
        '''
        Constructor
        '''
        self.model.add_notify(self)
        if self.fields == ():
            self.fields = [x for x in self.model.get_fields()]
            self.fields.remove(self.exclude_fields)

    def refresh(self):
        """docstring for dataChanged"""
        pass

    def clean(self):
        """Cleans temporary models of view"""
        raise NotImplementedError


    def save(self):
        """Saves models changes in view"""
        raise NotImplementedError
