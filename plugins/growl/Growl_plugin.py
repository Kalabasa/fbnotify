from PluginBase import PluginBase

import gntp.notifier

import time

class Plugin(PluginBase):
	''' Plugin for notifications using Growl '''

	_running = False
	_growl = None

	def plugin_init(self):
		# Register to Growl
		self._growl = gntp.notifier.GrowlNotifier(
			applicationName = 'fbnotify',
			notifications = ['Notification'],
			defaultNotifications = ['Notification']
		)
		self._growl.register()

		# Register to the 'notify' channel
		# to get messages about notifications
		handle = self._context.register_listener(self, 'notify')

		# Main loop
		self._running = True
		while self._context and self._running:
			# Call PluginResource.receive to get messages from the channel
			self._context.receive(handle)
			time.sleep(1)

	def plugin_destroy(self):
		# Stop the main loop
		self._running = False
		pass

	def plugin_dependencies(self):
		# No dependencies
		return []

	def plugin_receive(self, channel, **msg):
		# Receiving a message from the 'notify' channel

		# Show notification
		self._growl.notify(
			noteType = 'Notification',
			title = msg['title'],
			description = msg['body'],
			icon = msg['icon_data'],
			sticky = False,
			priority = 1,
		)