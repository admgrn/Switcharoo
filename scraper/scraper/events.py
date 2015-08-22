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


class EventsBase(object):
    def on_creating_node(self):
        print 'Creating new node in DB.'

    def on_node_exists(self):
        print 'Node exists'

    def on_adding_to_queue(self, url):
        print 'Adding ' + url + ' to queue.'

    def on_not_adding_to_queue(self, url):
        print 'Skipping ' + url + ' not adding to queue.'

    def waiting(self, seconds):
        print 'Waiting ' + str(seconds) + ' seconds for new submissions...'

    def on_clearing_cache(self):
        print "Clearing Cache"

    def using_url(self, url):
        print 'Using ' + url