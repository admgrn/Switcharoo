# Copyright 2015 Adam Greenstein <adamgreenstein@comcast.net>
# 
# Switcharoo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Switcharoo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Switcharoo.  If not, see <http://www.gnu.org/licenses/>.

import ConfigParser
from conf.configuration import get_config_file

class Conf:
    def __init__(self):
        config = ConfigParser.ConfigParser()
        config.read(get_config_file('config_scraper.ini'))
        self.db_host = config.get('db', 'host')
        self.db_username = config.get('db', 'username')
        self.db_password = config.get('db', 'password')
        self.auth = config.get('db', 'auth')
        self.share_port = int(config.get('db', 'share_port'))
        self.com_port = int(config.get('db', 'com_port'))
        self.r_username = config.get('reddit', 'username')
        self.r_password = config.get('reddit', 'password')