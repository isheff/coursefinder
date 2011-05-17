from __future__ import division
from facebook_app.models import *
import datetime

def update_rating_alg(request):
	
	# get all & courses
	Courses = Course.objects.all()
	# take two parts 
	Courses_list = list(Courses.order_by("id")[:700])
	while Courses.filter(id__gt = Courses_list[-1].id).count()!=0:
		Courses_list += list(Courses.filter(id__gt=Courses_list[-1].id)[:700])

	# Rating items
	Ratings = [Overall_Rating, Grading_Rating, Teaching_Rating]
        Course_Ratings = ['overall_avg', 'grading_avg', 'teaching_avg']
        Course_Rating_dict = dict(zip(Ratings,Course_Ratings))
	print "start to calculate"
	t0 = datetime.datetime.now()
	# calculate all averaging 
	for rating_item in Ratings:
		i=1#
		for course in Courses_list:
			course_rated = rating_item.objects.filter(course = course)
			course_alg = 0
			if len(course_rated)!=0:
				for each_rated in course_rated:
					course_alg += each_rated.value
				course_alg = course_alg/len(course_rated)
				setattr(course, Course_Rating_dict[rating_item] , course_alg)
				course.save()
			i+=1 #
			if i%20==0:
				print str((i/len(Courses_list))*100)+" %"


        delta_t = datetime.datetime.now()-t0
	return 'done, consumed '+str(delta_t)+' time'

