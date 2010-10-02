'''
@author: darvin
This module must be imported from django enviroment
'''

from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.handler import BaseHandler



class CollectionHandler(BaseHandler):
    exclude = ()
    allowed_methods = ('GET',)
    
    def read(self, request,  *args, **kwargs):
        filterargs = {}
        for arg in request.GET:
            filterargs[arg] = request.GET[arg]

        return self.model.objects.filter(**filterargs) 


def get_url_pattens(models):
    """Gets {"url":modelclass} dict, returns urls patterns"""

    urlpatterns = [url(r"^"+urlst,\
            Resource(type(model.__name__+"Handler", (CollectionHandler,), {"model":model})
                     )) for urlst, model in models.items()]
 

    return patterns("", * urlpatterns)
    
    
    