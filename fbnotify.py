#!/usr/bin/python
#
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

import notices
from Notifier import Notifier

import colorlog

import logging

if __name__ == '__main__':
	# Setup logger
	fh = logging.FileHandler('fbnotify.log')
	sh = logging.StreamHandler()
	formatter = colorlog.ColoredFormatter(
		"%(log_color)s[%(name)s] %(levelname)-8s %(message)s%(reset)s",
		datefmt=None,
		reset=True,
		log_colors={
			'DEBUG':    'cyan',
			'WARNING':  'yellow',
			'ERROR':    'red',
			'CRITICAL': 'bold_red',
		}
	)
	sh.setFormatter(formatter)
	
	root = logging.getLogger('')
	root.addHandler(fh)
	root.addHandler(sh)
	root.setLevel(logging.DEBUG)

	# Credits!
	print(notices.license)

	# Start!
	Notifier().start()
