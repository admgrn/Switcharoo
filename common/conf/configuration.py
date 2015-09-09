# Copyright 2015 Adam Greenstein <adamgreenstein@comcast.net>
# 
# common is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# common is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with common.  If not, see <http://www.gnu.org/licenses/>.

import os
import re

def get_config_file(filename=None, env='CONFLOC'):
    try:
        location = os.environ[env]
    except KeyError:
        location = ""
    if filename and not re.search('\.ini$', location):
        location = os.path.join(location, filename)
    return location