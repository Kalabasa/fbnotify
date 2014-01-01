class Item:
	''' a notification item '''

	# Should've been a named tuple instead of a class
	
	text = ''
	link = ''
	dt = None

	def __init__(self, text, link, dt):
		self.text = text
		self.link = link
		self.dt = dt