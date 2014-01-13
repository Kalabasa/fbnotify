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

from PluginContext import PluginContext

from Queue import Queue
import collections

import logging
logger = logging.getLogger(__name__)


PluginQueue = collections.namedtuple('PluginQueue', ['plugin', 'queue'])
PluginMessage = collections.namedtuple('PluginMessage', ['channel', 'message'])

class PluginMessageSystem:
	'''
	handles the messages sent to and between plugins
	'''

	_listeners = {}

	def register_plugin(self, plugin, channel):
		''' subscribes a plugin to a channel '''

		plugin_queue = self.find_plugin_queue(plugin)
		if not plugin_queue:
			queue = Queue()
			plugin_queue = PluginQueue(plugin, queue)
			plugin.context = PluginContext(self, plugin, queue)

		if not channel in self._listeners:
			self._listeners[channel] = []
		if not plugin_queue in self._listeners[channel]:
			self._listeners[channel].append(plugin_queue)

		return plugin.context

	def unregister_plugin(self, plugin):
		''' unregisters a plugin from all channels '''

		for c in self._listeners:
			l = self._listeners[c]
			l[:] = [q for q in l if q.plugin != plugin]

	def find_plugin_queue(self, plugin):
		''' return the PluginQueue associated with a plugin '''

		for c in self._listeners:
			for q in self._listeners[c]:
				if q.plugin == plugin:
					return q
		return None

	def send(self, channel, **kwargs):
		''' sends a message to all plugins subscribed to the channel '''

		pm = PluginMessage(channel, kwargs)
		if channel in self._listeners:
			for q in self._listeners[channel]:
				q.queue.put(pm)
