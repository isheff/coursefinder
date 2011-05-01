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



def populate_caltech_courses(request):
	message = ""
	
	# first, locate the caltech institution. 
	caltech = Institution.objects.filter(name="California Institute of Technology")
	if len(caltech)!=1:
		return "Too many or too few Caltechs!"
	caltech = caltech[0]
	
	#second, clear out all classes currently listed as caltech.
	for course in Course.objects.filter(institution = caltech):
		course.delete()
	
	# third, scrape us up a list of course names, numbers, and profs from the last 4 years.
	course_name_out = []
	course_prof_out = []
	course_numb_out = []

	terms=['FA','WI','SP']
	years = ['2007-08','2008-09','2009-10','2010-11']
	
	for year in years:
		for term in terms:
			# Import the catalog webpage
			data = urlopen('http://regis.caltech.edu/schedules/'+term+year+'.html')
			# Parse the contents
			soup = BeautifulSoup.BeautifulStoneSoup(data)

			#===========================================================
			course_name = soup.findAll(width="546")
			course_prof_all = soup.findAll(width=["192" , "83"] )
			course_numb = soup.findAll(width="128")
			course_prof_tag = soup.findAll(width="43" )
			soup2 = BeautifulSoup.BeautifulStoneSoup(str(course_numb))
			course_numb = soup2.findAll('a')
			#-==========================================================

			# Transfer course_name to contents only
			course_name_comments=[]
			for i in range(0,len(course_name)):
				course_name[i] = str(course_name[i].contents[0])
				if course_name[i].find('<i>')>= 0:
					course_name_comments.append(i)

			# delete comments in course_name
			for i in range(0,len(course_name_comments)):
				del course_name[course_name_comments[i]-i]
			# Remove empty course_name
			course_name=filter(lambda a: a !=' ',course_name)
			for i in range(0,len(course_name)):
				course_name_out.append(course_name[i])         #output

			# Transfer course_prof_all to contents only
			for i in range(0,len(course_prof_all)):
				course_prof_all[i]=str(course_prof_all[i].contents[0])
			# Remove empty course_prof
			course_prof_all=filter(lambda a: a !=' ',course_prof_all)

				
			# Transfer course_numb to contents only   
			for i in range(0,len(course_numb)):
				course_numb[i]=str(course_numb[i].contents[0])
				course_numb_out.append(course_numb[i])           #output
				
			# Find the first prof in multiful profs in course_prof_all
			course_prof_index=[]
			for i in range(0,len(course_prof_all)):
				if course_prof_all[i].find("-")== (course_prof_all[i].rfind("-")-2) or course_prof_all[i].find("-")== (course_prof_all[i].rfind("-")-3):
					course_prof_index.append(i+1)
				if course_prof_all[i].find("+")>=0:
					course_prof_index.append(i+1)
			course_prof = []
			# Get the first prof in course_prof
			for i in range(0,len(course_prof_index)):
				course_prof.append(course_prof_all[course_prof_index[i]])
			for i in range(0,len(course_prof)):
				course_prof_out.append(course_prof[i])         #output
		
		
		# some courses are annoying and have no space between department and number. we'll fix that:
		for i in range(len(course_numb_out)):
			coursenum = re.sub("\D", "", course_numb_out[i])
			course_numb_out[i] = re.sub(coursenum, " "+coursenum, course_numb_out[i])
		
		# now we have a list of course number, names, and profs with most recent last.
		# let's turn this into Course objects and Facebook_User objects for the instructors.
		coursedict = {}
		for course in range(len(course_name_out)):
			name = str(course_numb_out[course].split()[-1])+" "+str(course_name_out[course].strip())
			if not (name in coursedict):
				coursedict[name] = Course()
			coursedict[name].name = name
			#coursedict[name].description = ""
			coursedict[name].institution = caltech
			coursedict[name].department = map(lambda s: str(s.split()[0]), course_numb_out[course].split("/"))
			# get the course_description-------------------------------------------------------
			#course_dept_lower = [ w.lower() for w in coursedict[name].department]
			#for dept in course_dept_lower:
			#	data_des = urlopen('http://catalog.caltech.edu/courses/listing/'+dept+'.html')
			#	soup_des0 = BeautifulSoup.BeautifulStoneSoup(data_des)
			#	soup_des1 = BeautifulSoup.BeautifulStoneSoup(str(soup_des0.findAll("p", {"class":"course"})))
			#	target_course = soup_des1.find(text=re.compile(str( course_name_out[course].strip() ) ))
			#	course_description = target_course.findNext('span').string + target_course.findNext('span').findNext('span').string
			#	if len(course_description) > 250:
			#		course_description = course_description[:250]+" ..."                                                        
			#	if course_description.find('For course description')<0:
			#			break
			#	coursedict[name].description = course_description
			#--------------------------------------------------------------------------------
			teacher_names = map(lambda s: s.strip(), course_prof_out[course].split("/"))
			coursedict[name].teacher_ids = []
			for teacher_name in teacher_names:
				teacher = Facebook_User.objects.filter(name=teacher_name)
				if len(teacher) == 0:
					teacher = Facebook_User(name=teacher_name)
					teacher.save()
				else:
					teacher = teacher[0]
				coursedict[name].teacher_ids.append(int(teacher.id))
		for name in coursedict:
			coursedict[name].save()
		
		return " Success, I think. I got "+str(len(coursedict))+" courses."
			
			
	
	

