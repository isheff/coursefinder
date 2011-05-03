from dbindexer import autodiscover
autodiscover()

from facebook_app.models import Course
from dbindexer.api import register_index
register_index(Course,{'name':('icontains','contains')})
#register_index(Course,{'teacher':('icontains','contains')})
