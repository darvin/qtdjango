from django.conf import settings

from qtdjango.helpers import get_resource_name_for_model, get_all_models
from piston.resource import Resource
from handlers import create_handler_type
from django.conf.urls.defaults import url, patterns

def create_resource(model):
    """Builds resource from model class
    @param model: Model class"""

    return Resource(create_handler_type(model))

def get_url_pattens(app_list):
    """Gets app list returns urls patterns"""
    models = get_all_models(app_list, from_django=True)
    urlpatterns = [url(r"^"+get_resource_name_for_model(model),\
            create_resource(model)) for model in models]


    return patterns("", * urlpatterns)



urlpatterns = get_url_pattens(getattr(settings, "QTDJANGO_APPS" ))
