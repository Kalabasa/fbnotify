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

import Queue

import inspect # DEBUG

class PluginContext:
	'''
	this is where plugin interacts
	'''

	_context = None
	_plugin = None
	_queue = None

	def __init__(self, context, plugin, queue):
		self._context = context
		self._plugin = plugin
		self._queue = queue

	def register(self, channel):
		self._context.register_plugin(self._plugin, channel)

	def unregister(self, channel):
		self._context.unregister_plugin(self._plugin)

	def send(self, channel, **kwargs):
		''' sends a message to a channel '''

		self._context.send(channel, **kwargs)

	def receive(self):
		''' processes the message queue to receive messages '''

		try:
			while True:
				message = self._queue.get(False)
				self._plugin.plugin_receive(message.channel, message.message)
		except Queue.Empty:
			pass