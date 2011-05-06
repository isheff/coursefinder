from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('facebook_app.views',
    (r'^$', 'canvas'),
    (r'^canvas/$', 'canvas'),
    (r'^/$', 'canvas'),
    (r'^institution/(?P<institution_id>\d+)/$', 'display_institution'),
    (r'^course/(?P<course_id>\d+)/$', 'display_course'),
    (r'^course/(?P<course_id>\d+)/submit/$', 'rate_course'),
    (r'^data/(?P<user_id>\d+)/$', 'radar_chart'),
)

# the chart data views
urlpatterns += patterns('facebook_app.views',
    (r'^data/$','radar_chart'),
)
# the front page
urlpatterns += patterns('django.views.generic.simple',
    (r'^index/$', 'direct_to_template', {'template': 'test.html'}),
)
