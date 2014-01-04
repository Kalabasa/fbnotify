from PluginBase import PluginBase

import gtk
gtk.gdk.threads_init()

class Plugin(PluginBase):
	''' starts gtk.main '''

	def plugin_init(self):
		# Start gtk main loop
		gtk.main()

	def plugin_destroy(self):
		# Stop gtk
		gtk.main_quit()

	def plugin_receive(self, channel, message):
		pass
