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

import gntp.notifier

import time

class Plugin(PluginBase):
	''' shows notifications using Growl '''

	growl = None
	running = False

	def plugin_init(self):
		# Register to Growl
		self.growl = gntp.notifier.GrowlNotifier(
			applicationName = 'fbnotify',
			notifications = ['Errors', 'Notifications'],
			defaultNotifications = ['Errors', 'Notifications']
		)
		self.growl.register()

		# Wait for context
		while not self.context:
			pass

		# Main loop
		self.running = True
		while self.running:
			# Call PluginContext.receive to get messages
			self.context.receive()
			time.sleep(1)

	def plugin_destroy(self):
		# Stop the main loop
		self.running = False
		pass

	def plugin_receive(self, channel, message):
		# Receiving a message from the 'notify' channel

		# Show notification
		self.growl.notify(
			noteType = 'Notifications',
			title = message['title'],
			description = message['body'],
			icon = icons.icon_data,
			callback = message['link'],
			sticky = False,
			priority = 1,
		)