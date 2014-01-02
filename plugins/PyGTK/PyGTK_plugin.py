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