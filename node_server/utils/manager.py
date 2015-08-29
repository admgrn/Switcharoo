# Copyright 2015 Adam Greenstein <adamgreenstein@comcast.net>
# 
# node_server is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# node_server is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with node_server.  If not, see <http://www.gnu.org/licenses/>.

from socket import socket
from threading import Thread

class CacheManager:
    def __init__(self, fn):
        self.fn = fn
        self.server = None
        self.t = None

    def _reload_cache(self):
        self.fn()

    def _loop(self):
        self.server = socket()
        self.server.bind(('localhost', 5891))
        self.server.listen(1)
        while 1:
            connection, address = self.server.accept()
            value = connection.recv(32)
            if value.strip() == 'clear':
                self._reload_cache()
                connection.send('cleared')
            connection.close()

    def run(self):
        self.t = Thread(target=self._loop)
        self.t.start()
    def kill(self):
        if self.server:
            self.server.close()
        if self.t:
            self.t.kill()