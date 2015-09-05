# This file is part of fbnotify
#
# Copyright (c) 2014 Lean Rada <godffrey0@gmail.com>
# 
# fbnotify is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# fbnotify is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with fbnotify.  If not, see <http://www.gnu.org/licenses/>.

import urllib2
import hashlib
import uuid
import random
import time
import textwrap
import re
import os
import traceback

import logging
logger = logging.getLogger(__name__)


_user_matcher = re.compile(r'https?://www.facebook.com/n/\?(.+?)&')


class Item:
	''' a notification item '''

	id = None

	text = ''
	link = ''
	full = ''
	dt = None

	wrapped = None
	image_path = None

	def __init__(self, text, link, full, dt):
		self.id = uuid.uuid4();
		
		self.text = text
		self.link = link
		self.full = full
		self.dt = dt

		self.wrapped = textwrap.fill(text, 40)
		self.image_path = self.get_image()

	def get_image(self):
		# The get profile picture from username API was deprecated June 2015
		# Return nothing for now...
		return None

		# Get the first URL from the full text
		# Assuming that the first URL points to a user
		# Download the picture of that user
		images_directory = os.path.abspath('.')

		# Find the username
		user_match = _user_matcher.search(self.full)
		if not user_match:
			logger.warning('Did not understand URL ' + self.full)
			return None

		user = user_match.group(1)

		# Check if there is already a cached picture
		file_path = os.path.join(images_directory, hashlib.sha1(user).hexdigest())
		if os.path.isfile(file_path):
			if random.random() > 0.08:
				return file_path

		# Save the picture to cache
		try:
			logger.debug('Downloading image for ' + user + '...')
			size = 48
			image = urllib2.urlopen('http://graph.facebook.com/v2.4/' + user + '/picture?width={0}&height={0}'.format(size))
			f = open(file_path, 'w')
			f.write(image.read())
			f.close()
			os.chmod(file_path, 0600)
			time.sleep(1.5 * random.random())
		except IOError as e:
			logger.error(traceback.format_exc())
			return None

		return file_path
