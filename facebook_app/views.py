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
import pyofc2   
import random
import time

FACEBOOK_APP_ID = "174228859292999"
FACEBOOK_APP_SECRET = "cf8e2ce228f9a2d00f13357a826d0093"


@csrf_exempt
def canvas(request):
	user = get_current_user(request)
	institution = "California Institute of Technology" #for testing attendance
	attends_inst = attends_institution(user, institution)
	return render_to_response('facebook_app/canvas.html', {'current_user':user, 'facebook_app_id':FACEBOOK_APP_ID, 'institution':institution, 'attends_inst':attends_inst})

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
    """Returns whether the given user attends or has attended the given institution."""
    return True

    # Get user info.
    # TODO: do this in a more elegant way.
    try:
        graph = facebook.GraphAPI(user.access_token)
        profile = graph.get_object("me")
        # Get user's education history.	
        education_hist = profile["education"]
    except KeyError:
	    return False
    
	# Get user's institution(s). 
	#(Assume we have obtained permission to do so.  If we haven't, it will be blank anyway.)
	# We use names as primary identifiers for schools.
	
    user_institution_names = []
    for place in education:
        user_institution_names += place.school.name

    # Check whether given institution is in the user's education history.
    inst_name = institution.name
    return inst_name in user_institution_names
	
	# TODO: include possibility somewhere else for variability in institution name.
	# TODO: Elsewhere, let user know if they have no institutions listed.
    

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

# Radar chart for course-map

def radar_chart(request):
    
    chart = pyofc2.open_flash_chart() 
    chart.title = pyofc2.title(text='My course-map')
    chart.title.style =("{font-size:20px; color : #93998A;}")
    area = pyofc2.area_hollow()
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
    r = pyofc2.radar_axis(max=8)
    #------------------------------------------------------------
    r.colour ='#E5C994'     # main axis color
    r.grid_colour = '#E5C994'   # grid color
    ra = pyofc2.radar_axis_labels(labels=['','','2','','4','','6'])
    ra.colour = '#E5C994'   # label(on axis) color
    r.labels = ra
    
    # courses names----------------------------------------------
    sa = pyofc2.radar_spoke_labels(labels=['Computer<br>Science',
                                    'Electrical<br>Engineering',
                                    'Materials<br>Science',
                                    'Applied<br>Physics',
                                    'Humanity',
                                    'Math',
                                    'Physical<br>Education'])
    #------------------------------------------------------------
    sa.style="font-size:20px"
    sa.colour = '#FFF4BC'   # label color
    chart.radar_axis = r 
    r.spoke_labels = sa
    tip = pyofc2.tooltip()
    tip.proximity = 1
    chart.tooltip = tip
    chart.bg_colour = '#FFF4BC'
    return HttpResponse(chart.render())

    


