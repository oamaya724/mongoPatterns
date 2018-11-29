from django.conf.urls import url, include

from .views import *

urlpatterns =[
    url(r'^variables/$', variables),
    url(r'^variables/(?P<pk>\w+)/$', variablesDetail),
    url(r'^parqueaderos/$', parqueaderos),
    url(r'^parqueaderos/(?P<pk>\w+)/$', parqueaderoDetail),
    url(r'^warnings/$', warnings),
    url(r'^warnings/(?P<pk>\w+)/$', warningDetail),
    url(r'^warningsFilter/$', warningsFilter),
    url(r'^average/(?P<pk>\w+)/$', average)
]