
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
    always_read_only = False
    def __init__(self, verbose_name=None, *args, **kwargs):
        try:
            self.verbose_name = verbose_name
        except IndexError:
            self.verbose_name = ""
        self.__read_only =[]
        try:
            self.null = kwargs["null"]
        except KeyError:
            self.null = False
        try:
            self.blank = kwargs["blank"]
        except KeyError:
            self.blank = False


    def from_raw(self, data):
        return data

    def set_read_only_in(self, model_class):
        self.__read_only.append(model_class)

    def is_read_only_in(self, model_class):
        return (model_class in self.__read_only) or self.always_read_only

    def to_raw(self, data):
        return data

    def to_text(self, data):
        if data is None:
            return u"<пусто>"
        else:
            return unicode(data)

    def validate(self, data, model_instance):
        if data is None or data=="":
            if self.blank or self.null or self.is_read_only_in(model_instance.__class__):
                return None
            else:
                return u"Поле не может быть пустым"
        else:
            return None


    def get_blank(self):
        return None

    def get_label(self):
        try:
            return self.verbose_name
        except AttributeError:
            return "verbose name not defined"


class IdField(Field):
    always_read_only = True
    def __init__(self, *args, **kwargs):
        super(IdField, self).__init__(*args, **kwargs)
        self.read_only = True

    def load(self, data):
        return int(data)

class TextField(Field):
    pass

class HTMLField(TextField):
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

    def to_text(self, data):
        try:
            return data.strftime("%d.%m.%Y %H:%M")
        except AttributeError:
            return super(DateField, self).to_text(data)


class DateTimeField(DateField):
    def to_raw(self, data):
        return data.strftime("%Y-%m-%d %H:%M:%S")

class CharField(Field):
    pass


class URLField(CharField):
    def to_text(self, data):
        return u'<a href="%s">%s</a>' %(data, data)


class BooleanField(Field):
    pass
    def to_raw(self, data):
        return data

    def to_text(self, data):
        if data:
            return u"да"
        else:
            return u"нет"

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
#    def to_text(self, data):
#        return unicode(data)

    def to_raw(self, data):
        try:
            return data.id
        except AttributeError:
            return None



    def __init__(self, model, verbose_name=None, *args, **kwargs):
        super(ForeignKey, self).__init__(verbose_name=verbose_name, *args, **kwargs)
        self.model = model




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
        return u", ".join([unicode(item) for item in data])

    def to_raw(self, data):
        if not data:
            return []
        return [item.id for item in data]



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

    auto_user_fields = []


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


            for x in raw:
                o = cls(**x)
                o.__dumped=True
                o.version = cls.version
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
        cls.views = []
        for method in cls.exclude_methods:
            setattr(cls, method, getattr(Model, method))

        for methodname in dir(cls):
            try:
                if getattr(cls, methodname).method_as_field:
                    setattr(cls, methodname, getattr(cls, methodname).method_as_field)
                    getattr(cls, methodname).always_read_only = True
            except AttributeError:
                pass

        for field in cls.auto_user_fields+\
                     cls.read_only_fields:
            getattr(cls, field).set_read_only_in(cls)

        for fieldname, field in cls.get_rel_fields().items():
            #FIXME!
            try:
                field.model.reverse_sets
            except AttributeError:
                field.model.reverse_sets = {}
            setattr(field.model, cls.__name__.lower()+"_set",
                    lambda inst: cls.filter(**{fieldname:inst}))

    @classmethod
    def flush(cls):
        cls.objects = []
        cls.loaded = False


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
            if (fieldname!="id") and\
               (fieldname in self.auto_user_fields or not field.is_read_only_in(self.__class__) )\
                    and getattr(self, fieldname) is not None:
                d[fieldname]=unicode(field.to_raw(getattr(self, fieldname))).encode('utf-8')
        return d

    @classmethod
    def all(cls):
        return cls.filter()

    @classmethod
    def new(cls, **kwargs):
        """Used only from user code. Returns new model instance"""
        o = cls(**kwargs)
        o.__dumped = False
        o.id = cls.max_negative_undumped_id()
        cls.objects.append(o)
        return o

    def delete(self):
        """Deletes model instance"""
        self.__class__.objects.remove(self)
        self.notify()
        #FIXME real delete


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

    @classmethod
    def get_fields(cls):
        """
        Returns dict of class Fields           self.refresh()

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
                if "__" in field:
                    fs = field.split("__")
                    m = self
                    for i,f in enumerate(fs):
                        try:
                            m=getattr(m,f)
                        except AttributeError:
                            return False
                    if kwargs[field]!=m:
                        return False
                else:
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


    def validate(self):
        result = {}
        for fieldname, field in self.get_fields().items():
            result[fieldname]=field.validate(getattr(self, fieldname), self)
        return result


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
                setattr(self, fieldname, field.get_blank())



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
        for user_field_name in self.auto_user_fields:
            setattr(self, user_field_name, self.__models_manager.get_current_user())

        self.__dumped = False
        self.notify()

    @classmethod
    def add_notify(cls, view):
        """docstring for add_notify"""
        cls.views.append(view)

    def __unicode__(self):
        return "default unicode method"

    def extra_to_html(self):
        """
        Returns extra model-related objects, conventered to html
        """
        return ""

    @classmethod
    def max_negative_undumped_id(cls):
        max = 0
        for o in cls.objects:
            if o.id<max:
                max = o.id
        return max+1


class User(Model):
    resource_name = "django/users/"

    username = CharField(u"Имя пользователя", max_length=30, unique=True)
    first_name = CharField(u"Имя", max_length=30, blank=True)
    last_name = CharField(u"Фамилия", max_length=30, blank=True)
    email = EmailField(u"E-mail", blank=True)
    password = CharField(u"Пароль", max_length=128)
    is_staff = BooleanField(u"Статус персонала (доступ к админке)", default=False)
    is_active = BooleanField(u"Активный", default=True)
    is_superuser = BooleanField(u"Статус администратора", default=False)
    last_login = DateTimeField(u"Последний вход")
    date_joined = DateTimeField(u"Дата регистрации")
#    groups = models.ManyToManyField(Group, verbose_name=_('groups'), blank=True,
#       help_text=_("In addition to the permissions manually assigned, this user will also get all permissions granted to each group he/she is in."))
#    user_permissions = models.ManyToManyField(Permission, verbose_name=_('user permissions'), blank=True)
    class Meta:
        verbose_name = u"Пользователь"
        verbose_name_plural = u"Пользователи"

    def __unicode__(self):
        if self.last_name:
            return self.last_name
        else:
            return self.username

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
