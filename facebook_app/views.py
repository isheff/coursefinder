from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import Context, loader
from django.shortcuts import render_to_response, get_object_or_404
from django import forms
from django.forms import ValidationError
from django.core.context_processors import csrf
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from facebook_app.models import *
from urllib import urlopen
import BeautifulSoup,re
import facebook
import pyofc2   
import random
import time
from itertools import groupby
from course_value_convert import course_value_convert

FACEBOOK_APP_ID = "174228859292999"
FACEBOOK_APP_SECRET = "cf8e2ce228f9a2d00f13357a826d0093"


@csrf_exempt
def canvas(request):
        user = get_current_user(request)
        query_dept = request.POST.get('course_dept','')
        query_numb = request.POST.get('course_numb','')
        query_prof = request.POST.get('course_prof','')
        query_name = request.POST.get("course_name",'')
        
        if query_name:
               results= Course.objects.filter(name__icontains=query_name)
               
        elif query_dept:
                results= Course.objects.filter(department=query_dept)
                if query_numb:
                        results = results.filter(name__icontains=str(query_numb))
        #elif query_prof:
        #        results= Course.objects.filter(teacher__icontains=query_prof)
        else:
                results = []

        return render_to_response('facebook_app/canvas.html', {'current_user':user, 'facebook_app_id':FACEBOOK_APP_ID,"results":results })

def display_institution(request, institution_id):
        # TODO: edit template to display courses and stuff. 
        institute = get_object_or_404(Institution, id=int(institution_id))
        user = get_current_user(request)
        if attends_institution(user, institute):
                courses = Course.objects.filter(institution=institute)
                return render_to_response('facebook_app/display_institution.html', {'current_user':user, 'facebook_app_id':FACEBOOK_APP_ID, 'institution':institute, 'courses':courses})
        else:
                return HttpResponse("You do not attend this institution.")



@csrf_exempt
def rate_course(request, course_id):
        # this view, found at url "course/<course_id>/submit/", exists to recieve forms containing ONE of the following entries in form data:
        #
        # A Rating, Hours, or Grade:
        # Rating_Name: Overall_Rating, Grading_Rating, Hours, Grade, or Teacher_<teacher_id in this course.teacher_ids>_Rating
        # Rating_Value: some integer at least 1 appropriate for the number of stars or whatever for the Rating_Name's input
        #
        # A Course Comment:
        # Course_Comment_Text: the text of the comment
        # Course_Comment_Privacy: 0 for friends-only, 1 for public
        # 
        # A Teacher Comment:
        # Teacher_<teacher_id in this course.teacher_ids>_Comment_Text: the text of a comment by this user on this class with this teacher
        # Teacher_<teacher_id in this course.teacher_ids>_Comment_Privacy: 0 for friends-only, 1 for public
        #
        # If the form does not meet these specifications, the course does not exist, or the user does not attend the institution of the course, the 
        # page 404s, otherwise, it responds with a line of text to tell you your data was saved. 
        
        # first, let's get the course, user, and make sure the user attends the course's institution:
        p = get_object_or_404(Course, id=int(course_id))
        user=get_current_user(request)
        if attends_institution(user, p.institution):
                
                #now, just for bookeeping, if the course contains any teacher_ids not actually representative of teachers, delete them.
                for teacher_id in p.teacher_ids:
                        if len(Facebook_User.objects.filter(id=teacher_id)) == 0:
                                course.teacher_ids.remove(teacher_id)
                                course.save()
                
                # If a rating name was submitted, that means we're dealing with Overall_Rating, Grading_Rating, Hours, Grade, or Teacher_<teacher_id in this course.teacher_ids>_Rating
                if "Rating_Name" in request.REQUEST:
                        
                        # If an Overall_Rating was submitted, check to see if one exists, and overwrite it or create a new one.
                        if "Overall_Rating" == request.REQUEST["Rating_Name"] and "Rating_Value" in request.REQUEST:
                                if request.REQUEST["Rating_Value"] in ["1", "2", "3", "4", "5"]:
                                        over_rat = Overall_Rating.objects.filter(user=user, course=p)
                                        if len(over_rat)==0:
                                                over_rat = Overall_Rating( user=user, course=p)
                                        else:
                                                over_rat = over_rat[0]
                                        over_rat.value = (float(request.REQUEST["Rating_Value"])-1.0)/4.0
                                        over_rat.save()
                                        return HttpResponse("Overall Rating of "+str(over_rat.value)+" saved.")
                        
                        # If an Grading_Rating was submitted, check to see if one exists, and overwrite it or create a new one.
                        if "Grading_Rating" == request.REQUEST["Rating_Name"] and "Rating_Value" in request.REQUEST:
                                if request.REQUEST["Rating_Value"] in ["1", "2", "3", "4", "5"]:
                                        grad_rat = Grading_Rating.objects.filter(user=user, course=p)
                                        if len(grad_rat) == 0:
                                                grad_rat = Grading_Rating(user=user, course=p)
                                        else:
                                                grad_rat = grad_rat[0]
                                        grad_rat.value = (float(request.REQUEST["Rating_Value"])-1.0)/4.0
                                        grad_rat.save()
                                        return HttpResponse("Grading Rating of "+str(grad_rat.value)+" saved.")
                        
                        # If an Hours was submitted, check to see if one exists, and overwrite it or create a new one.
                        if "Hours" == request.REQUEST["Rating_Name"] and "Rating_Value" in request.REQUEST:
                                if request.REQUEST["Rating_Value"] in map(str, range(1, 21)):
                                        hours = Hours.objects.filter(user=user, course=p)
                                        if len(hours) == 0:
                                                hours = Hours(user=user, course=p)
                                        else:
                                                hours = hours[0]
                                        hours.hours = (int(request.REQUEST["Rating_Value"])-1)
                                        hours.save()
                                        return HttpResponse("Hours of "+str(hours.hours)+" saved.")
                        
                        # If a Grade was submitted, check to see if one exists, and overwrite it or create a new one.
                        if "Grade" == request.REQUEST["Rating_Name"] and "Rating_Value" in request.REQUEST:
                                if request.REQUEST["Rating_Value"] in ["1", "2", "3", "4", "5"]:
                                        grade = Grade.objects.filter(user=user, course=p)
                                        if len(grade) == 0:
                                                grade = Grade(user=user, course=p)
                                        else:
                                                grade = grade[0]
                                        grade.grade = (int(request.REQUEST["Rating_Value"])-1)
                                        grade.save()
                                        return HttpResponse("Grade of "+str(grade.grade)+" saved.")
                        
                        # Now, for each teacher, if a Teacher_Rating was submitted for that teacher, check to see if one exists, and overwrite it or create a new one.
                        for teacher_id in p.teacher_ids:
                                if "Teacher_"+str(teacher_id)+"_Rating" == request.REQUEST["Rating_Name"] and "Rating_Value" in request.REQUEST:
                                        if request.REQUEST["Rating_Value"] in ["1", "2", "3", "4", "5"]:
                                                teacher = Facebook_User.objects.get(id=teacher_id)
                                                teach_rat = Teaching_Rating.objects.filter(teacher=teacher, course=p, user=user)
                                                if len(teach_rat) == 0:
                                                        teach_rat=Teaching_Rating(teacher=teacher, course=p, user=user)
                                                else:
                                                        teach_rat = teach_rat[0]
                                                teach_rat.value = (float(request.REQUEST["Rating_Value"])-1.0)/4.0
                                                teach_rat.save()
                                                return HttpResponse("Teacher Rating of "+str(teach_rat.value)+" saved.")
                
                        
                # If an Course_Comment was submitted, check to see if one exists, and overwrite it or create a new one.
                if "Course_Comment_Text" in request.REQUEST:
                        com = Course_Comment.objects.filter(user=user, course=p)
                        if len(com) == 0:
                                com = Course_Comment(user=user, course=p)
                        else:
                                com = com[0]
                        com.content = request.REQUEST["Course_Comment_Text"]
                        com.privacy=int("Course_Comment_Privacy" in request.REQUEST) # i guess privacy 0 will be the "friends only" privacy level
                        com.save()
                        return HttpResponse("Comment "+str(com.content)+" saved.")
                
                # for each teacher if a Teacher_Comment was submitted, check to see if one exists, and overwrite it or create a new one.
                for teacher_id in p.teacher_ids:
                        comment_id = "Teacher_"+str(teacher_id)+"_Comment"
                        if comment_id+"_Text" in request.REQUEST:
                                teacher = Facebook_User.objects.get(id = teacher_id)
                                com = Teacher_Comment.objects.filter(teacher=teacher, user=user, course=p)
                                if len(com)==0:
                                        com = Teacher_Comment(teacher=teacher, user=user, course=p)
                                else:
                                        com = com[0]
                                com.content = request.REQUEST[comment_id+"_Text"]
                                com.privacy = int(comment_id+"_Privacy" in request.REQUEST)
                                com.save()
                                return HttpResponse("Comment "+str(com.content)+" saved.")
        # If no rating or comment was submitted that was findable or recordable, 404
        raise Http404



@csrf_exempt
def display_course(request, course_id):
        # This view returns a webpage in which a user can rate a class, comment on it, and do all those other things
        p = get_object_or_404(Course, id=int(course_id)) # The class to be displayed
        user=get_current_user(request) # the user presently logged in
        
        #First, we must assemble the necessary information to display in the form. This includes comments and ratings previously made by the User
        
        if attends_institution(user, p.institution): # The page should only be displayed if this User attends this Course's institution
                teachers = map(lambda x: Facebook_User.objects.get(id=x), p.teacher_ids) # the teachers teaching this course
                for teacher in range(len(teachers)):
                        # Any rating the user has previously given this teacher on this course must be passed to the template in the teacher object
                        tr = Teaching_Rating.objects.filter(user=user, course=p, teacher=teachers[teacher])
                        if len(tr) == 0:
                                teachers[teacher].user_rating=0
                        else:
                                teachers[teacher].user_rating = int(tr[0].value*4.0 + 1.1)
                        # Any comment teh user has previously given this teacher on this course must be passed to the template in the teacher object
                        cc = Teacher_Comment.objects.filter(teacher = teachers[teacher], user=user, course=p)
                        if len(cc) == 0:
                                teachers[teacher].course_comment=""
                                teachers[teacher].course_comment_privacy=0
                        else:
                                teachers[teacher].course_comment = cc[0].content
                                teachers[teacher].course_comment_privacy = int(cc[0].privacy)
                        # currently, we have no algorithm to predict ratings, so the predictions are all 0:
                        # note that predictions are displayed as % of 5 stars, so we must convert our 0-1 floats to 20-100%
                        teachers[teacher].rating = 0
                #The template will need the current user, the facebook_app_id, the course being rated, and the set of teachers for that course (with added info above)
                pass_to_template = {'current_user':user, 'facebook_app_id':FACEBOOK_APP_ID, 'course':p}
                pass_to_template['teachers'] = teachers
                # Any Overall Rating previously input by the user must be passed to the template
                over_rat = Overall_Rating.objects.filter(user=user, course=p)
                if len(over_rat) == 0:
                        pass_to_template['User_Overall_Rating']=0
                else:
                        pass_to_template['User_Overall_Rating']=int(over_rat[0].value*4.0 + 1.1)
                # Any Grading Rating previously input by the user must be passed to the template
                grad_rat = Grading_Rating.objects.filter(user=user, course=p)
                if len(over_rat) == 0:
                        pass_to_template['User_Grading_Rating']=0
                else:
                        pass_to_template['User_Grading_Rating']=int(grad_rat[0].value*4.0 + 1.1)
                #Any Course Comment previously input by the user must be passed to the template
                course_com = Course_Comment.objects.filter(user=user, course=p)
                if len(course_com) == 0:
                        pass_to_template['Course_Comment'] = ""
                        pass_to_template['Course_Comment_Privacy'] = 0
                else:
                        pass_to_template['Course_Comment'] = course_com[0].content
                        pass_to_template['Course_Comment_Privacy'] = int(course_com[0].privacy)
                # Any Hours previously input by the User must be passed to the template
                hours = Hours.objects.filter(user=user, course=p)
                if len(hours)==0:
                        pass_to_template['Hours'] = 0
                else:
                        pass_to_template['Hours'] = hours[0].hours+1
                # Any Grade Previously input by the user must be passed to the Template
                grade = Grade.objects.filter(user=user, course=p)
                if len(grade) == 0:
                        pass_to_template['Grade'] = 0
                else:
                        pass_to_template['Grade'] = grade[0].grade + 1
                # currently, we have no algorithm to predict ratings, so the predictions are 0:
                # note that predictions are displayed as % of 5 stars, so we must convert our 0-1 floats to 20-100%
                pass_to_template['Overall_Rating'] = 0
                pass_to_template['Grading_Rating'] = 0
                return render_to_response('facebook_app/display_course.html', pass_to_template)
        else:
                return HttpResponse("You do not attend this institution.")

def attends_institution(user, institution):
        #TODO: make this method return whether the given user attends the given institution.
        return True

def get_current_user(request):
        user = None
        
        
        # FOR OFF-GOOGLE TESTING ONLY***************
        #return get_object_or_404(Facebook_User, name="Isaac")
        # FOR OFF-GOOGLE TESTING ONLY***************
        
        
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

# radar chart for course-map

def radar_chart(request,user_key_name):
    user=get_current_user(request) # the user presently logged in
    user_key_name = user.key_name
    user_name = user.name
    user_current = Overall_Rating.objects.filter(user=user)
    user_dept=[]
    for i in range(len(user_current)):
	    user_dept.append(user_current[i].course.department)
    #--------------------------------------------------------------------------
    # 1. convert dept list to value&name lists
    [course_taken_fullname,course_taken_value]=course_value_convert(user_dept)        
    # 2. max courses have taken in one dept
    course_value_max=round(max(course_taken_value))
    if course_value_max %2!=0: course_value_max += course_value_max
    if course_value_max <8: course_value_max = 8
    # 3. make labels
    course_value_label = []
    for i in range(course_value_max):
	    if i%2==0:
		    course_value_label.insert(i,str(i))
	    else:
		    course_value_label.insert(i,'')
	    course_value_label[0]=''

    #--------------------------------------------------------------------------
    chart = pyofc2.open_flash_chart() 
    chart.title = pyofc2.title(text=user.name+"'s  course-map")
    chart.title.style =("{font-size:20px; color : #B0BFBA;}")   # title colour
    area = pyofc2.area_hollow()
    area.width = 1
    area.dot_size = 1
    area.halo_size = 1
    area.colour = '#B0BFBA'         # area edge color
    area.fill_colour = '#FFFFFF'    # area color
    area.fill_alpha = 0.5
    area.loop = True
    
    area.values = course_taken_value
    chart.add_element(area) 

    r = pyofc2.radar_axis(max=course_value_max,steps=2)
    r.colour ='#36647F'     # main axis color
    r.grid_colour = '#36647F'   # grid color
    ra = pyofc2.radar_axis_labels(labels=course_value_label,size=12)
    ra.colour = '#B0BFBA'   # label(on axis) color
    r.labels = ra
    
    sa = pyofc2.radar_spoke_labels(labels=course_taken_fullname ,size=40)
    
    sa.colour = '#B0BFBA'   # label color
    chart.radar_axis = r 
    r.spoke_labels = sa
    tip = pyofc2.tooltip()
    tip.proximity = 1
    chart.tooltip = tip
    chart.bg_colour = '#3B3B40' # background color
    return HttpResponse(chart.render())
