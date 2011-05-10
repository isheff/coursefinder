# my_filters.py
# Additional custom filters
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

