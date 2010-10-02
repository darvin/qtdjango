# Preambula
QtDjango is library to connect to django-piston powered server and use it's models in PyQt application

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

Then, install django piston and make you models avaible throuth it. Your `urls.py` and `handlers.py` must looks like mine: [urls.py](http://github.com/darvin/cryotec-service/blob/master/cryotec_service/api/urls.py) [handlers.py](http://github.com/darvin/cryotec-service/blob/master/cryotec_service/api/handlers.py) (this will be done automagically in future.)

That's all with server-side

## Client side

### Models

Import you models transparently from you django application package:

   from qtdjango.models import load_from_django
   models = load_from_django("your base package of server", ["list","of","application","names"])

Or just import its from pyqt client application.
You will cat sealessly throuth net make django-like calls:

   from mycoolproject.myapp.models import MyModel
   from qtdjango.models import register
   register(MyModel)
   MyModel.get(1).one_field
   x = MyModel.filter("one_field"=12,"foreinkeyfield__foreign_keys_field"="some value")
   x[0].foreingkeyfield.foreing_keys_field
