# THIS FILE CONTAINS THINGS ABOUT ICONS

import os

_program_dir = os.path.dirname(os.path.realpath(__file__))

xdg_icon = 'facebook'

icon_path = os.path.join(_program_dir, 'icons/22/icon.png')
icon_new_path = os.path.join(_program_dir, 'icons/22/icon-new.png')
icon_error_path = os.path.join(_program_dir, 'icons/22/icon-error.png')

icon_data = open(icon_path, 'rb').read() if icon_path else None
icon_new_data = open(icon_new_path, 'rb').read() if icon_new_path else None
icon_error_data = open(icon_error_path, 'rb').read() if icon_error_path else None
