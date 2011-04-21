from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from django import forms
from django.forms import ValidationError
from django.core.context_processors import csrf
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from facebook_app.models import Facebook_User, Institution, Course
from urllib import urlopen
import BeautifulSoup,re
import facebook
from pyofc2  import * 
import random
import time

FACEBOOK_APP_ID = "174228859292999"
FACEBOOK_APP_SECRET = "cf8e2ce228f9a2d00f13357a826d0093"


@csrf_exempt
def canvas(request):
	user = get_current_user(request)
	return render_to_response('facebook_app/canvas.html', {'current_user':user, 'facebook_app_id':FACEBOOK_APP_ID})

def display_institution(request, institution_id):
	# TODO: edit template to display courses and stuff. 
	institute = get_object_or_404(Institution, id=int(institution_id))
	user = get_current_user(request)
	if attends_institution(user, institute):
		courses = Course.objects.filter(institution=institute)
		return render_to_response('facebook_app/display_institution.html', {'current_user':user, 'facebook_app_id':FACEBOOK_APP_ID, 'institution':institute, 'courses':courses})
	else:
		return HttpResponse("You do not attend this institution.")
	
	

def display_course(request, course_id):
	# TODO: Add form processing so reviews care added to database
	# TODO: edit template so people can actually review course
	p = get_object_or_404(Course, id=int(course_id))
	user=get_current_user(request)
	if attends_institution(user, p.institution):
		return render_to_response('facebook_app/display_course.html', {'current_user':user, 'facebook_app_id':FACEBOOK_APP_ID, 'course':p, 'teachers':map(lambda x: Facebook_User.objects.get(id=x), p.teacher_ids)})
	else:
		return HttpResponse("You do not attend this institution.")

def attends_institution(user, institution):
	#TODO: make this method return whether the given user attends the given institution.
	return True

def get_current_user(request):
	user = None
	cookie = facebook.get_user_from_cookie(request.COOKIES, FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)
	if cookie:
		user = Facebook_User.objects.filter(key_name=cookie["uid"])
		if len(user) == 0:
			graph = facebook.GraphAPI(cookie["access_token"])
			profile = graph.get_object("me")
			user = Facebook_User(key_name=str(profile["id"]),
				name=profile["name"],
				profile_url=profile["link"],
				access_token=cookie["access_token"])
			user.save()
		else:
			user = user[0]
			if user.access_token != cookie["access_token"]:
				user.access_token = cookie["access_token"]
				user.save()
	return user

# dadar chart for course-map

def radar_chart(request):
    
    chart = open_flash_chart() 
    chart.title = title(text='My course-map')
    chart.title.style =("{font-size:20px; color : #93998A;}")
    area = area_hollow()
    area.width = 1
    area.dot_size = 1
    area.halo_size = 1
    area.colour = '#2E2E33'         # area edge color
    area.fill_colour = '#CC6622'    # area color
    area.fill_alpha = 0.4
    area.loop = True
    
    # values of courses taken-----------------
    area.values = [3, 4, 5, 4, 3, 3, 2.5]
    #-----------------------------------------
    chart.add_element(area) 

    # Max courses have taken in one dept (choose max=8)----------  
    r = radar_axis(max=8)
    #------------------------------------------------------------
    r.colour ='#E5C994'     # main axis color
    r.grid_colour = '#E5C994'   # grid color
    ra = radar_axis_labels(labels=['','','2','','4','','6'])
    ra.colour = '#E5C994'   # label(on axis) color
    r.labels = ra
    
    # courses names----------------------------------------------
    sa = radar_spoke_labels(labels=['Computer<br>Science',
                                    'Electrical<br>Engineering',
                                    'Materials<br>Science',
                                    'Applied<br>Physics',
                                    'Humanity',
                                    'Math',
                                    'Physecal<br>Education'])
    #------------------------------------------------------------
    sa.style="font-size:20px"
    sa.colour = '#FFF4BC'   # label color
    chart.radar_axis = r 
    r.spoke_labels = sa
    tip = tooltip()
    tip.proximity = 1
    chart.tooltip = tip
    chart.bg_colour = '#FFF4BC'
    return HttpResponse(chart.render())

    


