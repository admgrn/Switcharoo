# Copyright 2015 Adam Greenstein <adamgreenstein@comcast.net>
# 
# web is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# web is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with web.  If not, see <http://www.gnu.org/licenses/>.
from multiprocessing.managers import BaseManager

class CacheClient:
    def __init__(self, port, auth):
        self.port = port
        self.auth = auth

    def get_cache(self):
        manager = BaseManager(address=('', self.port), authkey=self.auth)
        manager.register('get_cache')
        manager.connect()
        return manager.get_cache()