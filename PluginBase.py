class PluginBase:
	''' base class for plugins '''

	_resource = None
	__thread = None

	def plugin_init(self):
		''' initialize anything here '''
		raise NotImplementedError()

	def plugin_destroy(self):
		''' cleanup everything here '''
		raise NotImplementedError()

	def plugin_dependencies(self):
		'''
		must return a list of plugin names that must be initialized
		before initializing this plugin
		'''
		raise NotImplementedError()

	def plugin_receive(self, **kwargs):
		''' called to receive a message from the plugin messaging system '''
		pass