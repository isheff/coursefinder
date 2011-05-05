from django.db import models
from djangotoolbox.fields import ListField
from django.utils.html import escape
from datetime import datetime

# Create your models here.


class DateStamped(models.Model):
	"""
	This is an abstract class (you can't actually make and store these) designed so that classes which inherit it
	have creation and update timestamps.
	"""
	created = models.DateTimeField(auto_now_add=True)	# date upon which this object was created
	updated = models.DateTimeField(auto_now=True)		# latest update time to this object
	
	class Meta:
		abstract = True


class Facebook_User(DateStamped):
	"""
	This is the class for a facebook user, as defined by Facebook's Python-SDK google appengine example
	
	I added a title, for use with teachers, and made the facebook-provided fields optionally blank, so 
	Teachers can be created as Facebook_Users without actually knowing their facebook info. 
	"""
	title = models.CharField(max_length=100, blank=True, default="")		# user's title (optional, default "")
	name = models.CharField(max_length=100)									# user's name 
	key_name = models.CharField(max_length=100, blank=True, default="")		# users's facebook ID
	profile_url = models.CharField(max_length=200, blank=True, default="")	# user's profile's URL
	access_token = models.CharField(max_length=255, blank=True, default="")	# user's oauth access token (facebook defined, changes)
	
	def __unicode__(self):
		"""
		This method defines how this class is converted to a string (for example, in the admin interface)
		"""
		return str(self.title)+" "+str(self.name)


class Institution(DateStamped):
	"""
	This model represents a university or college, or whatever else offers classes.
	"""
	name = models.CharField(max_length=255)												# Insititution's Name
	description = models.CharField(max_length=1023)										# Insititution's Description
	url = models.URLField(verify_exists=True, max_length=255, blank=True, default="")	# a url for this university. (optional)
	
	def __unicode__(self):
		"""
		This method defines how this class is converted to a string (for example, in the admin interface)
		"""
		return self.name


class Course(DateStamped):
	"""
	This model represents a Course offered at a university of college.
	"""
	name = models.CharField(max_length=255)												# Course Name
	description = models.CharField(max_length=1023)										# Course Description
	institution = models.ForeignKey('Institution', related_name="Courses_Institution")	# the institution offering this course
	url = models.URLField(verify_exists=True, max_length=255, blank=True, default="")	# a url for this course. (optional)
	department = ListField(models.CharField(max_length=100))							# a list of this course's departments. 
	teacher = ListField(models.CharField(max_length=200))
	teacher_lastname=ListField(models.CharField(max_length=(200)))
	#	Not sure if this is the best way to store this
	teacher_ids = ListField(models.IntegerField())										# a list of ids of teacher models teaching this course
	
	def __unicode__(self):
		"""
		This method defines how this class is converted to a string (for example, in the admin interface)
		"""
		return self.name


class User_Course_Interaction(DateStamped):
	"""
	This is an abstract model, meaning you can't actually create and save these, designed to define the required fields for
	every other model which featers a user and a course. (comments, ratings, etc . . . )
	"""
	user = models.ForeignKey('Facebook_User',  related_name="%(app_label)s_%(class)s_student_user")	# the user involved. 
	course = models.ForeignKey('Course')															# the course involved
	date = models.DateField(auto_now=False, auto_now_add=False, default = datetime.now().date())	# ideally the date the class was taken. default: now
	
	class Meta:
		abstract = True


class Comment(User_Course_Interaction):
	"""
	This is an abstract model, meaning you can't actually create and save these, designed to define the required fields for
	every other Comment based model
	"""
	content = models.CharField(max_length=1023)	# Comment text
	privacy = models.IntegerField()				# Comment privacy rating. Not sure how we'll standardize this, but it should be an integer
	
	def __unicode__(self):
		"""
		This method defines how this class is converted to a string (for example, in the admin interface)
		"""
		return str(self.user.name) + ", "+str(self.course.name)+": "+str(self.content)[:30]
	
	class Meta:
		abstract = True


class Course_Comment(Comment):
	"""
	A course comment, at the moment at least, has nothing more than a generic comment.
	"""
	pass


class Teacher_Comment(Comment):
	"""
	A comment on a teacher, for a class.
	"""
	teacher = models.ForeignKey('Facebook_User')		# the Teacher involved. 


class Rating(User_Course_Interaction):
	"""
	This is an abstract model, meaning you can't actually create and save these, designed to define the required fields for
	every other model for Rating Courses.
	"""
	value = models.FloatField()	# the value of a rating is a float. Let's standardize now. 0 is bad. 1 is good. Rate however you want.	
	def __unicode__(self):
		"""
		This method defines how this class is converted to a string (for example, in the admin interface)
		"""
		return str(self.user.name) + ": "+str(self.value)+" " +str(self.course.name)
	
	class Meta:
		abstract = True


class Overall_Rating(Rating):
	"""
	This is the overall rating for a course. It is just a rating. Nothing to add.
	"""
	pass


class Grading_Rating(Rating):
	"""
	This is the Grading rating for a course. It is just a rating. Nothing to add.
	
	I'm not entirely sure this is the most useful thing. It's not that it's not a useful measure, it's just that next to courses and
	teachers, it's just yet another thing . . . 
	"""
	pass


class Teaching_Rating(Rating):
	"""
	This is the teaching rating for a course, and a teacher. It is a rating, but now with both a course and a teacher.
	"""
	teacher = models.ForeignKey('Facebook_User')		# the Teacher involved.




# below are classes talked about as being potentially useful, but perhaps not part of our core model. 

class Hours(User_Course_Interaction):
	"""
	This is a model for recording the number of hours a user spent on a course
	"""
	hours = models.IntegerField()	# The number of hours the user spent on the course
	
	def __unicode__(self):
		"""
		This method defines how this class is converted to a string (for example, in the admin interface)
		"""
		return str(self.user.name) + ", "+str(self.course.name)+": "+str(self.hours)

class Grade(User_Course_Interaction):
	"""
	This is a model for recording the grade a user got in a course
	"""
	grade = models.IntegerField()	# The grade a user got in a course 0=F, 1=D, 2=C, 3=B, 4=A
	
	def __unicode__(self):
		"""
		This method defines how this class is converted to a string (for example, in the admin interface)
		"""
		return str(self.user.name) + ", "+str(self.course.name)+": "+str(self.grade)
