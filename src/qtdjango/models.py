
# -*- coding: UTF-8 -*-

'''
@author: darvin
'''





from inspect import getmro
import json


def istype(obj, typename):
    try:
        return typename in [clsobj.__name__ for clsobj in getmro(obj.__class__)]
    except AttributeError:
        return False

class Field(object):
    widget = None
    def __init__(self, verbose_name=None, *args, **kwargs):
        try:
            self.verbose_name = verbose_name
        except IndexError:
            pass
        self.read_only = False

    def from_raw(self, data):
        return data

    def to_raw(self, data):
        return data

    def to_text(self, data):
        return unicode(data)

    def blank(self):
        return None

    def get_label(self):
        try:
            return self.verbose_name
        except AttributeError:
            return "verbose name not defined"


class IdField(Field):
    def __init__(self, *args, **kwargs):
        super(IdField, self).__init__(*args, **kwargs)
        self.read_only = True

    def load(self, data):
        return int(data)

class TextField(Field):
    pass

from datetime import datetime
class DateField(Field):
    def from_raw(self, data):
        try:
            return datetime.strptime(data, "%Y-%m-%d")
        except ValueError:
            return datetime.strptime(data, "%Y-%m-%d %H:%M:%S")
    def to_raw(self, data):
        return data.strftime("%Y-%m-%d")

class DateTimeField(DateField):
    pass

class CharField(Field):
    pass



class BooleanField(Field):
    pass
    def to_raw(self, data):
        return data

class EmailField(CharField):
    pass
    def to_raw(self, data):
        raise NotImplementedError


class FileField(CharField):
    pass
    def to_raw(self, data):
        raise NotImplementedError

class IntegerField(Field):
    def from_raw(self, data):
        if data is not None:
            return int(data)
        else:
            return None

    def to_raw(self, data):
        if data is not None:
            return int(data)
        else:
            return None


class PositiveIntegerField(IntegerField):
    pass

class RelField(Field):
    pass

class ForeignKey(RelField):

    def from_raw(self, data):
        if data is not None:
            if self.model.loaded:
                return self.model.get(data["id"])
            else:
                return data
        else:
            return None
    def to_text(self, data):
        return unicode(data)

    def to_raw(self, data):
        try:
            return data.id
        except AttributeError:
            return None


    def __init__(self, model, verbose_name=None, *args, **kwargs):
        super(ForeignKey, self).__init__(verbose_name=verbose_name, *args, **kwargs)
        self.model = model
#        self.model.load()
#        self.model.__setattr__("foreing_key_model_"+kwargs["self"].__name__, kwargs["self"])



class ManyToManyField(ForeignKey):
    def from_raw(self, data):

        if data is not None:
            if self.model.loaded:
                try:
                    res = []
                    for item in data:
                        res.append(self.model.get(item["id"]))
                    return res
                except TypeError:
                    return data
            else:
                return data
        else:
            return None
    def to_text(self, data):
            return unicode(data)

    def to_raw(self, data):
        raise NotImplementedError



class ResourceNameError(Exception):
    pass


class Model(object):
    '''
    classdocs
    '''
    resource_name = None
    """@cvar: This is resource name of model"""

    loaded = False
    """@cvar: This is flag, is model loaded"""

    __models_manager = None
    """@cvar: This is ModelManager object, throuth that model
    works with remote Django server"""

    objects = []
    """@cvar: List of Model instances of this model"""

    views = []
    """@cvar: List of views, connected to this model"""

    exclude_methods = ("save",)
    """@cvar: List of methods of models, that must be subtitude by Model class methods"""

    read_only_fields = []
    """@cvar: List of fields to read-only"""

    include_methods_results = {}
    """@cvar: Dict of methods to fetch from server"""

    dump_order = 0
    """@cvar: Order to dump"""

    @classmethod
    def load(cls):
        """Loads all model objects from server via ModelsManager.
        Sets initial [] values for objects and views"""
        if not cls.loaded:
            if cls.resource_name is None:
                raise ResourceNameError
            cls.id = IdField("Id")
            raw = cls.__models_manager.get_resource_from_server(cls.resource_name)
            cls.objects = []
            cls.views = []
            cls.max_negative_undumped_id = -1
            """@cvar Current maximal undumped id"""
            for x in raw:
                o = cls(**x)
                o.__dumped=True
                cls.objects.append(o)
            cls.loaded = True
    #FIXME
    @classmethod
    def refresh_foreing_keys(cls):
        for obj in cls.objects:
            for fieldname in dir(cls):
                if isinstance(getattr(cls,fieldname), ForeignKey):
                    if not istype(getattr(obj, fieldname), "Model"):
                        setattr(obj, fieldname,\
                                getattr(cls, fieldname).from_raw(getattr(obj, fieldname)))

    @classmethod
    def init_model_class(cls, models_manager):
        """
        Inits model class, sets ModelsManager for Model class
        @param models_manager: ModelsManager object
        """
        cls.__models_manager = models_manager
        for method in cls.exclude_methods:
            setattr(cls, method, getattr(Model, method))

        for method in cls.include_methods_results:
            setattr(cls, method, cls.include_methods_results[method])

        for field in cls.read_only_fields+cls.include_methods_results.keys():
            getattr(cls, field).read_only = True

    @classmethod
    def dump(cls):
        """
        Dumps all new model instances to server
        @return: list of responces dict
        """
        if cls.resource_name is None:
                raise ResourceNameError
        else:
            responces = []
            for o in cls.objects:
                if not o.is_dumped():
                    r = o.to_raw()
                    resp = cls.__models_manager.post_resource_to_server(cls.resource_name, args=r)
                    responces.append(resp)
                    if resp["headers"]["status"]=="200":
                        body = json.loads(resp["body"])
                        o.__refresh(**body)
                        o.__dumped=True
                    elif resp["headers"]["status"]=="400":
                        o.__valid = False

            cls.notify()
            return responces


    def to_raw(self):
        """Returns raw model instance representation"""
        d = {}
        for fieldname, field in self.__class__.get_fields().items():
            if fieldname!="id" and not field.read_only and getattr(self, fieldname) is not None:
                d[fieldname]=unicode(field.to_raw(getattr(self, fieldname))).encode('utf-8')
        from pprint import pprint
        pprint(d)
        return d

    @classmethod
    def all(cls):
        return cls.filter()

    @classmethod
    def new(cls, **kwargs):
        """Used only from user code. Returns new model instance"""
        o = cls(**kwargs)
        o.__dumped = False
        o.id = cls.max_negative_undumped_id
        cls.max_negative_undumped_id-=1
        cls.objects.append(o)
        return o

    @classmethod
    def verbose_name(cls, plural=False):
        """Returns verbose name of model
        @param plural: return plural verbose name"""
        if plural:
            try:
                return cls.Meta.verbose_name_plural
            except AttributeError:
                return cls.__name__
        else:
            try:
                return cls.Meta.verbose_name
            except AttributeError:
                return cls.__name__+"s"

    @classmethod
    def filter(cls, **kwargs):
        return [x for x in cls.objects if x.is_filtered(**kwargs)]

    @classmethod
    def get(cls, id):
        res = cls.filter(id=id)
        if len(res)==1:
            return res[0]
#    def foreign_set(self, setname):
#        try:
#            fclass = "foreing_key_model_"+setname
#        except KeyError:
#            print setname
#            print globals()
#            pass 
#        return fclass.filter(\
#                    **{self.__class__.__name__.lower():self})
    @classmethod
    def get_fields(cls):
        """
        Returns dict of class Fields
        """
        f = {}
        for fieldname in dir(cls):
            if istype(getattr(cls, fieldname), "Field"):
                f[fieldname] = getattr(cls, fieldname)
        return f

    @classmethod
    def get_rel_fields(cls):
        """
        Returns dict of relative (Foreign keys, etc) Fields
        """
        f = {}
        for fieldname in dir(cls):
            field = getattr(cls, fieldname)
            try:
                if RelField in getmro(field.__class__):
                    f[fieldname] = getattr(cls, fieldname)
            except AttributeError:
                pass

        return f



    @staticmethod
    def is_model_depend_on(one_class, other_class):
        """
        Returns True, if class has references to another class
        """
#        print one_class , "<=>" , other_class
        for field in one_class.get_rel_fields().values():
            if field.model==other_class:
#                print one_class , "depend on" , other_class
                return 1
        return -1

    @staticmethod
    def is_model_instance_depend_on(model_instance, other_model_instance):
        """
        Returns True, if model instance has references to another class
        """
        for fieldname, field in model_instance.get_rel_fields().items():
            if getattr(model_instance, fieldname)==other_model_instance:
                return 1
        return -1

    def is_filtered(self, **kwargs):
        for field in kwargs:
            try:
                try:
                    if not getattr(self, field) in kwargs[field]:
                        return False
                except TypeError:
                    if not getattr(self, field)==kwargs[field]:
                        return False
            except AttributeError:
                #FIXME to any number of folding
                if "__" in field:
                    try:
                        keymodel, keyfield = field.split("__")
                        if getattr(getattr(self,keymodel),keyfield)!=kwargs[field]:
                            return False
                    except ValueError:
                        keymodel, keyfield, keyfield2 = field.split("__")
                        if getattr(getattr(getattr(self,keymodel),keyfield),keyfield2)!=kwargs[field]:
                            return False
                else:
                    print field, self
                    raise KeyError
        return True

    def is_dumped(self):
        """
        Returns True if model instance was dumped to server or was fetched from server
        """
        return self.__dumped

    def is_valid(self):
        """
        Returns False if model instance failed validation
        """
        return self.__valid


    @classmethod
    def is_all_dumped(cls):
        """
        Returns True if all Model instances is dumped to server
        (there is not unsaved objects)
        """
        for obj in cls.objects:
            if not obj.is_dumped():
                return False
        return True

    def __init__(self, **initdict):
        super(Model,self).__init__()
#        print initdict
        self.__valid = True
        """@ivar __valid: False if model instance failed validation"""
        self.__refresh(**initdict)

    def __refresh(self, **initdict):
        self.__valid = True
        for fieldname, field in self.__class__.get_fields().items():
            try:
                setattr(self, fieldname, field.from_raw(initdict[fieldname]))
            except KeyError:
                setattr(self, fieldname, field.blank())


    @classmethod
    def notify(cls):
        """Sends notify to all views, connected to model"""
        for v in cls.views:
            v.refresh()
        if not cls.is_all_dumped():
            cls.__models_manager.notify_changes()

    def save(self):
        """
        Saves object
        """

        self.__dumped = False
        self.notify()

    @classmethod
    def add_notify(cls, view):
        """docstring for add_notify"""
        cls.views.append(view)

    def __unicode__(self):
        return "default unicode method"



class User(Model):
    #Todo: implement django behavoir
    resource_name = "django/users/"
    username = CharField() 
    first_name = CharField()
    
if __name__=="__main__":
    
    
#    from cryotec_service.machines.models import *
#    from cryotec_service.clients.models import *
#    Machine.load()
# 
#    print Machine.fields
#    
#    
#    print Machine.resource_name
#    print Client.resource_name
#    print Client.get(1).name
#    print Machine.get(1).serial
#    print Machine.get(1).motohours
    pass
