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

class PluginBase:
	''' base class for plugins '''

	context = None

	def plugin_init(self):
		'''
		initialize anything that is needed

		This method can run only until plugin_destroy is called. When 
		plugin_destroy is called, this method must terminate.
		'''
		raise NotImplementedError()

	def plugin_destroy(self):
		'''
		cleanup everything that needs to be cleaned up before shutting down
		'''
		raise NotImplementedError()

	def plugin_receive(self, channel, message):
		'''
		called when receiving a message from the plugin messaging system
		'''
		raise NotImplementedError()