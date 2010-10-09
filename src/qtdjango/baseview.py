
# -*- coding: utf-8 -*-
class BaseView(object):
    '''
    classdocs
    '''
    fields = ()
    widgets = {}
    model = None

    def __init__(self, **kwargs):
        '''
        Constructor
        '''
        self.model.add_notify(self)
        if self.fields == ():
            self.fields = [x for x in self.model.get_fields()]

    def refresh(self):
        """docstring for dataChanged"""
        pass

