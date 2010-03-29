from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns(
  'gheimdall2.idp.views',
  url(r'^static_login$', 'static_login', name='static_login'),
  url(r'^login$', 'login', name='login'),
  url(r'^login.do$', 'login_do', name='login_do'),
  url(r'^logout$', 'logout', name='logout'),
  url(r'^passwd$', 'password', name='passwd'),
  url(r'^passwd.do$', 'passwd_do', name='passwd_do'),
  url(r'^admin/reset_password$', 'reset_password', name='reset_password'),
  url(r'^admin/reset_password.do$', 'reset_password_do',
      name='reset_password_do'),
  url(r'^ga_pixel$', 'ga_pixel', name='ga_pixel'),
)

if settings.DEBUG:
  urlpatterns += patterns('',
                          (r'^static/(?P<path>.*)$', 'django.views.static.serve',
                          {'document_root': settings.STATIC_DOC_ROOT}))
