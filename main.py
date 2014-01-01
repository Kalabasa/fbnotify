#!/usr/bin/env python

from Notifier import Notifier
import logging

if __name__ == '__main__':
	logging.basicConfig(format='[%(name)s] %(levelname)s: %(message)s', level=logging.DEBUG)
	Notifier().start()
