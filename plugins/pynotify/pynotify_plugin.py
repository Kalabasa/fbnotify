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

from PluginBase import PluginBase
import icons

import pynotify

import time

import logging
logger = logging.getLogger(__name__)


class Plugin(PluginBase):
	''' shows notifications using pynotify '''

	running = False

	def plugin_init(self):
		# Initialize pynotify
		pynotify.init('fbnotify')

		# Wait for context
		while not self.context:
			pass

		# Main loop
		self.running = True
		while self.running:
			# Call PluginContext.receive to get messages
			self.context.receive()
			time.sleep(1)

		# Done
		pynotify.uninit()

	def plugin_destroy(self):
		# Stop the main loop
		self.running = False

	def plugin_receive(self, channel, message):
		# Receiving a message from the 'notify' channel

		# Show notification
		n = pynotify.Notification(message['title'], message['body'], message['icon'])
		if 'timeout' in message:
			n.set_timeout(message['timeout'] * 1000)

		if not n.show():
			logger.error('Failed to show notification')
