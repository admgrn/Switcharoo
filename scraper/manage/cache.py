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

from socket import socket


def clear_cache():
    client = socket()
    client.connect(('localhost', 5891))
    client.send('clear')
    data = client.recv(32)
    status = data.strip() == 'cleared'
    client.close()
    return status

