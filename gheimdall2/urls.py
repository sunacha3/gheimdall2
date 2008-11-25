from django.conf.urls.defaults import *
from django.conf import settings
# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns(
  '',
  # Example:
  # (r'^gheimdall2/', include('gheimdall2.foo.urls')),
  # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
  # to INSTALLED_APPS to enable admin documentation:
  #(r'^admin/doc/', include('django.contrib.admindocs.urls')),
  # Uncomment the next line to enable the admin:
  #(r'^admin/(.*)', admin.site.root),
  (r'^login$', 'gheimdall2.idp.views.login'),
  (r'^login.do$', 'gheimdall2.idp.views.login_do'),
  (r'^logout$', 'gheimdall2.idp.views.logout'),
  (r'^passwd$', 'gheimdall2.idp.views.password'),
  (r'^passwd.do$', 'gheimdall2.idp.views.passwd_do'),
)

if settings.DEBUG:
  urlpatterns += patterns('',
                          (r'^static/(?P<path>.*)$', 'django.views.static.serve',
                          {'document_root': settings.STATIC_DOC_ROOT}))
