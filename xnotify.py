try:
	import pynotify
except ImportError:
	pynotify = None

try:
	import gtk
	import gobject
	gobject.threads_init()
except ImportError:
	gtk = None

from threading import Thread

class SysNotif:
	def __init__(self, app_name):
		# Initialize notification library
		pynotify.init(app_name)
		self.app_name = app_name

		if gtk:
			self._init_gtk()

	def _init_gtk(self):
		# Create status icon in notification area
		self.gtk_notif_icon = si = gtk.StatusIcon()
		si.set_from_icon_name('facebook')
		si.set_visible(True)

		# Start gtk.main
		self.gtk_thread = Thread(target=gtk.main)
		self.gtk_thread.daemon = True
		self.gtk_thread.start()

	def stop(self):
		if gtk:
			gtk.main_quit()
			self.gtk_thread.join()

	def send(self, title, message, icon=None, wxicon=None, urgency=None, timeout=None):
		if pynotify:
			n = pynotify.Notification(title, message, icon)
			if urgency:
				n.set_urgency(getattr(pynotify, 'URGENCY_%s' % urgency.upper()))
			if timeout:
				n.set_timeout(timeout)
			n.show()

	def set_tooltip(self, text):
		if gtk:
			self.gtk_notif_icon.set_tooltip(text)