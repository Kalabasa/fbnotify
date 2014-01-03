Facebook Notifier
=================

**fbnotify** ~~is~~ will be a cross-platform Facebook notifier using Python. 

This is still in-development!

It runs in the background and notifies you whenever you get a notification in Facebook. Notifications come to you instead of you coming for them.

Installation
------------

Simply copy everything to any directory.

Usage
-----

Use at your own risk. This is a work-in-progress.

To run, execute `main.py` (`./main.py` or `python main.py`).

To stop, use an interrupt signal (`^C` on *nix)

Plugins
-------

There is a plugin system to aid in making it cross-platform.

* pynotify
	
	Plugin to handle notifications using libnotify.

* PyGTK

	Plugin for displaying the status icon in the notification area

* Growl
	
	**UNTESTED** Plugin for showing notifications using Growl


Libraries
=========

Libraries included are listed here. Files are listed as well.

* [ActiveState/appdirs](https://github.com/ActiveState/appdirs) to get configuration directory
	* appdirs.py
	* appdirs.pyc
* [borntyping/python-colorlog](https://github.com/borntyping/python-colorlog) for colorful logging
	* colorlog/colorlog.py
	* colorlog/escape_codes.py

License
=======

This software is released under the **GNU General Public License** (GPL) which
can be found in the file **LICENSE** in the same directory as this file.

Licenses for the included libraries can be found in the same directory in the files **_name_.LICENSE** where _name_ is the name of the library.