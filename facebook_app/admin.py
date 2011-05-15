from facebook_app.models import *
from django.contrib import admin

#note that all the non-abstract models are here, except Course. Course has listfields, which the admin interface can't handle.
admin.site.register(Institution)
admin.site.register(Course_Comment)
admin.site.register(Teacher_Comment)
admin.site.register(Overall_Rating)
admin.site.register(Grading_Rating)
admin.site.register(Teaching_Rating)
admin.site.register(Hours)
admin.site.register(Grade)