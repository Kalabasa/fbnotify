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

		# Main loop
		self._running = True
		while self.context and self._running:
			# Call PluginContext.receive to get messages
			self.context.receive()
			time.sleep(1)

	def plugin_destroy(self):
		# Stop the main loop
		self._running = False
		pass

	def plugin_receive(self, channel, message):
		# Receiving a message from the 'notify' channel

		# Show notification
		self._growl.notify(
			noteType = 'Notification',
			title = message['title'],
			description = message['body'],
			icon = message['icon_data'],
			sticky = False,
			priority = 1,
		)