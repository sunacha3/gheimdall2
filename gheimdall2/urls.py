from django.conf.urls.defaults import *
from django.conf import settings
# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns(
  'gheimdall2.idp.views',
  # Example:
  # (r'^gheimdall2/', include('gheimdall2.foo.urls')),
  # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
  # to INSTALLED_APPS to enable admin documentation:
  #(r'^admin/doc/', include('django.contrib.admindocs.urls')),
  # Uncomment the next line to enable the admin:
  #(r'^admin/(.*)', admin.site.root),
  (r'^static_login$', 'static_login'),
  (r'^login$', 'login'),
  (r'^login.do$', 'login_do'),
  (r'^logout$', 'logout'),
  (r'^passwd$', 'password'),
  (r'^passwd.do$', 'passwd_do'),
  (r'^admin/reset_password$', 'reset_password'),
  (r'^admin/reset_password.do$', 'reset_password_do'),
)

if settings.DEBUG:
  urlpatterns += patterns('',
                          (r'^static/(?P<path>.*)$', 'django.views.static.serve',
                          {'document_root': settings.STATIC_DOC_ROOT}))
