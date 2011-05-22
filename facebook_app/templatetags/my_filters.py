# my_filters.py
# Additional custom filters
import re
from django.utils.encoding import force_unicode
from django.template.defaultfilters import register

@register.filter(name = "lookup")
def lookup(dict, index):
	if index in dict:
		return dict[index]
	return ''

@register.filter(name="truncatechars")
def truncatechars(s, num):
    	"""
    	Truncates a word after a given number of chars  
    	Argument: Number of chars to truncate after
    	"""
    	length = int(num)
    	string = []
    	for word in s.split():
        	if len(word) > length:
            		string.append(word[:length]+'...')
      		else:
           		string.append(word)
	return u' '.join(string)
@register.filter(name="removefirstword")
def removefirstword(s):
	s = force_unicode(s)
	words = s.split()
	if len(words) >1:
		words = words[1:]
	return u' '.join(words)
@register.filter(name="onlyfirstword")
def onlyfirstword(s):
        s = force_unicode(s)
        words = s.split()
        if len(words)>1:
                words = words[:1]
        return u' '.join(words)
@register.filter(name="unit2percent")
def unit2percent(num):
        if num == 0.0:
                result = int(0)
        else:
                result = int(num*80+20)
        return result
