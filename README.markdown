# Preambula
QtDjango is library to connect to django-piston powered server and use it's models in PyQt application

# Downloads

[http://pypi.python.org/pypi/qtdjango/]

# Installing

    easy_install qtdjango

# Using

## Server side

### Models modification

First of all, you need make some modifications of your models.
Replace this line in every `models.py` file:

    from django.db import models

by lines:

    try:
        from django.db import models
    except ImportError:
        from qtdjango import models

Then, install django-piston and add qtdjango.
Add to your `settings.py`:
    INSTALLED_APPS += 'qtdjango.django_qtdjango'
    #list of apps that must be passed throught qtdjango api
    QTDJANGO_APPS = ( "list", "of", "apps")

Add to your `urls.py`:
    urlpatterns = patterns(
       #.... some urls ....
       #qtdjango api url
       (r'^api/', include('qtdjango.django_qtdjango.urls')),
     )

That's all with server-side

## Client side

### Models

Import you models transparently from you django application package:

    from qtdjango.models import load_from_django
    models = load_from_django("your base package of server", ["list","of","application","names"])

    from qtdjango.modelsmanager import ModelsManager

    ADDRESS = "http://127.0.0.1:8000"
    API_PATH= "/api/"
    mm = ModelsManager(ADDRESS, API_PATH, "/path/to/your/django/project", \
                              ["list", "of", "apps"],)
    
    current_module =__import__(__name__)
    mm.do_models_magic_with_module(current_module)

Then, `mm` object will load models from django server.
You could create some module, for example, `models.py` in your PyQt client applications, and put in it that code. Then, you will coult access to model classes like `from models import MyModel`

You will can sealessly throuth net make django-like calls:

    MyModel.get(1).one_field
    x = MyModel.filter("one_field"=12,"foreinkeyfield__foreign_keys_field"="some value")
    x[0].foreingkeyfield.foreing_keys_field
