from qtdjango.piston_handlers import get_url_pattens
from django.conf import settings


urlpatterns = get_url_pattens(getattr(settings, "QTDJANGO_APPS" ))
