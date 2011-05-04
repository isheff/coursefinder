from __future__ import division
from operator import itemgetter
import random

def course_value_convert(user_dept):

    single_dept=[]
    single_value=[]
    multi_dept=[]
    multi_value=[]
    course_value={}
    course_taken_fullname=[]
    course_taken_value=[]
    course_default=['EE','CS','ACM','ME','Ma','Ec','MS','Ph']
    # splitting dept list into "single" or "multiple"
    for i in range(len(user_dept)):
                if isinstance(user_dept[i],list):
                          for dept in user_dept[i]:
                                multi_dept.append(dept)
                                multi_value.append(float(1/len(user_dept[i])))
                else:
                         single_dept.append(user_dept[i])
                         single_value.append(1)
    unique_dept = list(set(single_dept + multi_dept))
    # make course_default distinct
    course_default = [ x for x in course_default if not x in unique_dept]
    # adding value of each department
    for unique in unique_dept:
        course_value[unique]=0
        for i in range(len(single_dept)):
            if single_dept[i] == unique:
                course_value[unique]+=single_value[i]
        for i in range(len(multi_dept)):
            if multi_dept[i] == unique:
                course_value[unique]+=multi_value[i]
        course_value[unique] = "%.2f" %course_value[unique]
    #sorting
    course_value_sort = sorted(course_value.iteritems(),key=itemgetter(1),reverse=True)
    #truncate
    del course_value_sort[7:]
    # random shuffle
    random.shuffle(course_value_sort)
    # add default department with value=0
    if len(course_value_sort)<7:
	    for i in range(7-len(course_value_sort)):
		    course_value_sort.append([course_default[i],0])

    # fullname dictionary for dept
    fullname = {'Ae':'Aerospace',
                'An':'Anthropology',
                'ACM':'Applied and Computational Mathematics',
                'AM':'Applied Mechanics',
                'APh':'',
                'Art':'Art History',
                'Ay':'Astrophysics',
                'BMB':'Biochemistry and Molecular Biophysics',
                'BE':'Bioengineering',
                'Bi':'Biology',
                'BEM':'Business Economics and Management',
                'ChE':'Chemical Engineering',
                'Ch':'Chemistry',
                'CE':'Civil Engineering',
                'CNS':'Computation and Neural Systems',
                'CS':'Computer Science',
                'CDS':'Control and Dynamical Systems',
                'Ec':'Economics',
                'EE':'Electrical Engineering ',
                'EST':'Energy Science and Technology',
                'E':'Engineering',
                'En':'English',
                'ESL':'English As a Second Language',
                'ESE':'Environmental Science and Engineering',
                'F':'Film',
                'Ge':'Geological and Planetary Sciences',
                'H':'History',
                'HPS':'History and Philosophy of Science',
                'Hum':'Humanities',
                'ISP':'Independent Studies Program',
                'IST':'Information Science and Technology',
                'L':'Languages',
                'Law':'Law',
                'MS':'Materials Science',
                'Ma':'Mathematics',
                'ME':'Mechanical Engineering',
                'Mu':'Music',
                'PA':'Performance and Activities',
                'PI':'Philosophy',
                'PE':'Physical Education',
                'Ph':'Physics',
                'Ps':'Political Science',
                'Psy':'Psychology',
                'SS':'Social Science',
                }
    # transfer fullname into multiple lines for pyofc2
    for key in fullname:
	    fullname[key]=fullname[key].replace(' and','&')
	    fullname[key]=fullname[key].replace(' ','<br>')
	    fullname[key]=fullname[key].replace('&',' &')

    # get the fullname 
    for i in range(len(course_value_sort)):
        course_taken_fullname.append(fullname.get(course_value_sort[i][0],course_value_sort[i][0]))
        course_taken_value.append(float(course_value_sort[i][1]))
    return course_taken_fullname,course_taken_value
