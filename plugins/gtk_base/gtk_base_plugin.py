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

import gtk

class Plugin(PluginBase):
	''' starts gtk.main '''

	def plugin_init(self):
		gtk.gdk.threads_init()
		# Start gtk main loop
		gtk.main()

	def plugin_destroy(self):
		# Stop gtk
		gtk.main_quit()

	def plugin_receive(self, channel, message):
		pass
