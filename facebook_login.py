#!/usr/bin/env python
# coding: utf-8
# Copyright 2011 Facebook, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#	 http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import os
# dummy config to enable registering django template filters
os.environ[u'DJANGO_SETTINGS_MODULE'] = u'conf'

from google.appengine.dist import use_library
#use_library('django')

from django.template.defaultfilters import register
from django.utils import simplejson as json
from functools import wraps
from google.appengine.api import urlfetch, taskqueue
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import util, template
from google.appengine.runtime import DeadlineExceededError
from random import randrange
from uuid import uuid4
import Cookie
import base64
import cgi
#import conf
import datetime
import hashlib
import hmac
import logging
import time
import traceback
import urllib
from facebook_app.models import Facebook_User as User

FACEBOOK_APP_ID = "174228859292999"
FACEBOOK_APP_SECRET = "cf8e2ce228f9a2d00f13357a826d0093"


def htmlescape(text):
	"""Escape text for use as HTML"""
	return cgi.escape(
		text, True).replace("'", '&#39;').encode('ascii', 'xmlcharrefreplace')


@register.filter(name=u'get_name')
def get_name(dic, index):
	"""Django template filter to render name"""
	return dic[index].name


@register.filter(name=u'get_picture')
def get_picture(dic, index):
	"""Django template filter to render picture"""
	return dic[index].picture


def select_random(lst, limit):
	"""Select a limited set of random non Falsy values from a list"""
	final = []
	size = len(lst)
	while limit and size:
		index = randrange(min(limit, size))
		size = size - 1
		elem = lst[index]
		lst[index] = lst[size]
		if elem:
			limit = limit - 1
			final.append(elem)
	return final










class FacebookApiError(Exception):
	def __init__(self, result):
		self.result = result

	def __str__(self):
		return self.__class__.__name__ + ': ' + json.dumps(self.result)


class Facebook(object):
	"""Wraps the Facebook specific logic"""
	def __init__(self, app_id=FACEBOOK_APP_ID,
			app_secret=FACEBOOK_APP_SECRET):
		self.app_id = app_id
		self.app_secret = app_secret
		self.user_id = None
		self.access_token = None
		self.signed_request = {}

	def api(self, path, params=None, method=u'GET', domain=u'graph'):
		"""Make API calls"""
		if not params:
			params = {}
		params[u'method'] = method
		if u'access_token' not in params and self.access_token:
			params[u'access_token'] = self.access_token
		result = json.loads(urlfetch.fetch(
			url=u'https://' + domain + u'.facebook.com' + path,
			payload=urllib.urlencode(params),
			method=urlfetch.POST,
			headers={
				u'Content-Type': u'application/x-www-form-urlencoded'})
			.content)
		if isinstance(result, dict) and u'error' in result:
			raise FacebookApiError(result)
		return result

	def load_signed_request(self, signed_request):
		"""Load the user state from a signed_request value"""
		try:
			sig, payload = signed_request.split(u'.', 1)
			sig = self.base64_url_decode(sig)
			data = json.loads(self.base64_url_decode(payload))

			expected_sig = hmac.new(
				self.app_secret, msg=payload, digestmod=hashlib.sha256).digest()

			# allow the signed_request to function for upto 1 day
			if sig == expected_sig and \
					data[u'issued_at'] > (time.time() - 86400):
				self.signed_request = data
				self.user_id = data.get(u'user_id')
				self.access_token = data.get(u'oauth_token')
		except ValueError, ex:
			pass # ignore if can't split on dot

	@property
	def user_cookie(self):
		"""Generate a signed_request value based on current state"""
		if not self.user_id:
			return
		payload = self.base64_url_encode(json.dumps({
			u'user_id': self.user_id,
			u'issued_at': str(int(time.time())),
		}))
		sig = self.base64_url_encode(hmac.new(
			self.app_secret, msg=payload, digestmod=hashlib.sha256).digest())
		return sig + '.' + payload

	@staticmethod
	def base64_url_decode(data):
		data = data.encode(u'ascii')
		data += '=' * (4 - (len(data) % 4))
		return base64.urlsafe_b64decode(data)

	@staticmethod
	def base64_url_encode(data):
		return base64.urlsafe_b64encode(data).rstrip('=')


class CsrfException(Exception):
	pass


class LoginHandler():
	facebook = None
	user = None
	csrf_protect = True

	def initialize(self, request):
		"""General initialization for every request"""
		#super(BaseHandler, self).initialize(request, response)
		self.headers = {}
		self.request = request
		try:
			self.init_facebook()
			self.init_csrf()
			self.headers[u'P3P'] = u'CP=HONK'  # iframe cookies in IE
		except Exception, ex:
			self.log_exception(ex)
			raise

	def handle_exception(self, ex, debug_mode):
		"""Invoked for unhandled exceptions by webapp"""
		self.log_exception(ex)
		raise ex

	def log_exception(self, ex):
		"""Internal logging handler to reduce some App Engine noise in errors"""
		msg = ((str(ex) or ex.__class__.__name__) +
				u': \n' + traceback.format_exc())
		if isinstance(ex, urlfetch.DownloadError) or \
		   isinstance(ex, DeadlineExceededError) or \
		   isinstance(ex, CsrfException) or \
		   isinstance(ex, taskqueue.TransientError):
			logging.warn(msg)
		else:
			logging.error(msg)

	def set_cookie(self, name, value, expires=None):
		"""Set a cookie"""
		if value is None:
			value = 'deleted'
			expires = datetime.timedelta(minutes=-50000)
		jar = Cookie.SimpleCookie()
		jar[name] = value
		jar[name]['path'] = u'/'
		if expires:
			if isinstance(expires, datetime.timedelta):
				expires = datetime.datetime.now() + expires
			if isinstance(expires, datetime.datetime):
				expires = expires.strftime('%a, %d %b %Y %H:%M:%S')
			jar[name]['expires'] = expires
		jarHeader = jar.output().split(u': ', 1)
		self.headers[jarHeader[0]] = jarHeader[1]

	def init_facebook(self):
		"""Sets up the request specific Facebook and User instance"""
		facebook = Facebook()
		user = None

		# initial facebook request comes in as a POST with a signed_request
		if u'signed_request' in self.request.POST:
			facebook.load_signed_request(self.request.get('signed_request'))
			# we reset the method to GET because a request from facebook with a
			# signed_request uses POST for security reasons, despite it
			# actually being a GET. in webapp causes loss of request.POST data.
			self.request.method = u'GET'
			self.set_cookie(
				'u', facebook.user_cookie, datetime.timedelta(minutes=1440))
		elif 'u' in self.request.cookies:
			facebook.load_signed_request(self.request.COOKIES.get('u'))

		# try to load or create a user object
		if facebook.user_id:
			user = User.objects.filter(key_name=facebook.user_id)
			if len(user)>0:
				user=user[0]
				# update stored access_token	
				if facebook.access_token and \
						facebook.access_token != user.access_token:
					user.access_token = facebook.access_token
					user.save()
				# refresh data if we failed in doing so after a realtime ping
				#if user.dirty:
				user.refresh_data()
				# restore stored access_token if necessary
				if not facebook.access_token:
					facebook.access_token = user.access_token

			if len(user)==0 and facebook.access_token:
				me = facebook.api(u'/me', {u'fields': _USER_FIELDS})
				try:
					friends = [user[u'id'] for user in me[u'friends'][u'data']]
					user = User(key_name=facebook.user_id, friends=friends,
						access_token=facebook.access_token, name=me[u'name'],
						email=me.get(u'email'), picture=me[u'picture'])
					user.save()
				except KeyError, ex:
					pass # ignore if can't get the minimum fields

		self.facebook = facebook
		self.user = user

	def init_csrf(self):
		"""Issue and handle CSRF token as necessary"""
		self.csrf_token = self.request.COOKIES.get(u'c')
		if not self.csrf_token:
			self.csrf_token = str(uuid4())[:8]
			self.set_cookie('c', value=self.csrf_token)
		if self.request.method == u'POST' and self.csrf_protect and \
				self.csrf_token != self.request.POST.get(u'_csrf_token'):
			raise CsrfException(u'Missing or invalid CSRF token.')

	def set_message(self, **obj):
		"""Simple message support"""
		self.set_cookie('m', value = base64.b64encode(json.dumps(obj)) if obj else None)

	def get_message(self):
		"""Get and clear the current message"""
		message = self.request.cookies.get(u'm')
		if message:
			self.set_message()  # clear the current cookie
			return json.loads(base64.b64decode(message))

"""
def user_required(fn):
	#Decorator to ensure a user is present
	@wraps(fn)
	def wrapper(*args, **kwargs):
		handler = args[0]
		if handler.user:
			return fn(*args, **kwargs)
		handler.redirect(u'/')
	return wrapper




class RealtimeHandler(BaseHandler):
	#Handles Facebook Real-time API interactions
	csrf_protect = False

	def get(self):
		if (self.request.GET.get(u'setup') == u'1' and
			self.user and conf.ADMIN_USER_IDS.count(self.user.user_id)):
			self.setup_subscription()
			self.set_message(type=u'success',
				content=u'Successfully setup Real-time subscription.')
		elif (self.request.GET.get(u'hub.mode') == u'subscribe' and
			  self.request.GET.get(u'hub.verify_token') ==
				  conf.FACEBOOK_REALTIME_VERIFY_TOKEN):
			self.response.out.write(self.request.GET.get(u'hub.challenge'))
			logging.info(
				u'Successful Real-time subscription confirmation ping.')
			return
		else:
			self.set_message(type=u'error',
				content=u'You are not allowed to do that.')
		self.redirect(u'/')

	def post(self):
		body = self.request.body
		if self.request.headers[u'X-Hub-Signature'] != (u'sha1=' + hmac.new(
			self.facebook.app_secret,
			msg=body,
			digestmod=hashlib.sha1).hexdigest()):
			logging.error(
				u'Real-time signature check failed: ' + unicode(self.request))
			return
		data = json.loads(body)

		if data[u'object'] == u'user':
			for entry in data[u'entry']:
				taskqueue.add(url=u'/task/refresh-user/' + entry[u'id'])
				logging.info('Added task to queue to refresh user data.')
		else:
			logging.warn(u'Unhandled Real-time ping: ' + body)

	def setup_subscription(self):
		path = u'/' + conf.FACEBOOK_APP_ID + u'/subscriptions'
		params = {
			u'access_token': conf.FACEBOOK_APP_ID + u'|' +
							 conf.FACEBOOK_APP_SECRET,
			u'object': u'user',
			u'fields': _USER_FIELDS,
			u'callback_url': conf.EXTERNAL_HREF + u'realtime',
			u'verify_token': conf.FACEBOOK_REALTIME_VERIFY_TOKEN,
		}
		response = self.facebook.api(path, params, u'POST')
		logging.info(u'Real-time setup API call response: ' + unicode(response))



class RefreshUserHandler(BaseHandler):
	#Used as an App Engine Task to refresh a single user's data if possible
	csrf_protect = False

	def post(self, user_id):
		logging.info('Refreshing user data for ' + user_id)
		user = User.get_by_key_name(user_id)
		if not user:
			return
		try:
			user.refresh_data()
		except FacebookApiError:
			user.dirty = True
			user.put()


def main():
	routes = [
		(r'/', RecentRunsHandler),
		(r'/user/(.*)', UserRunsHandler),
		(r'/run', RunHandler),
		(r'/realtime', RealtimeHandler),

		(r'/task/refresh-user/(.*)', RefreshUserHandler),
	]
	application = webapp.WSGIApplication(routes,
		debug=os.environ.get('SERVER_SOFTWARE', '').startswith('Dev'))
	util.run_wsgi_app(application)


if __name__ == u'__main__':
	main()
"""