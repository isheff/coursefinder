from django.conf.urls.defaults import *

urlpatterns = patterns('facebook_app.views',
    (r'^$', 'canvas'),
    (r'^canvas/$', 'canvas'),
    (r'^/$', 'canvas'),
    (r'^institution/(?P<institution_id>\d+)/$', 'display_institution'),
    (r'^course/(?P<course_id>\d+)/$', 'display_course'),
)