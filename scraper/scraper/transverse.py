# Copyright 2015 Adam Greenstein <adamgreenstein@comcast.net>
#
# Switcharoo Cartographer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Switcharoo Cartographer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Switcharoo Cartographer.  If not, see <http://www.gnu.org/licenses/>.

import praw

from data import Access
from entryqueue import EntryQueue
from manage.cache import clear_cache
from manage.config import Conf
from source import Source

from multiprocessing.managers import BaseManager


class Transverse:
    def __init__(self, events):
        config = Conf()
        self.reddit = praw.Reddit(user_agent='Switcharoo Cartographer v.0.2.1')
        self.reddit.login(config.r_username, config.r_password, disable_warning=True)
        self.events = events
        self.queue = None
        self.data = Access(self.events)
        self.source = Source(self)
        self._port = config.com_port
        self._share_port = config.share_port
        self._auth = config.auth
        self._should_stop = False
        self._threshold = 10

    def init_queue(self):
        if self.queue is None:
            self.queue = EntryQueue(self)

    def build_graph(self, current_entry):
        entry_point = True
        stop = False
        found = False
        found_list = []
        while current_entry is not None and not stop:
            current_entry.set_next()
            if current_entry.next_entry is None and entry_point:
                self.source.mark_searched(current_entry)
                return found, found_list
            entry_point = False
            # Check if item is already in graph
            node, stop = self.data.is_new_node(current_entry)
            # New node
            if not stop:
                found = True
                found_list.append(node)
            parents = self.data.get_parents(current_entry)
            for parent in parents:
                created = self.data.add_link(parent, node)
                if created:
                    found = True
            self.source.mark_searched(current_entry)
            current_entry = current_entry.next_entry
        return found, found_list

    def analyze_found(self, list):
        if len(list) > 0:
            manager = BaseManager(address=('', self._share_port), authkey=self._auth)
            manager.register('get_meta_data')
            manager.connect()
            distances, max_dist = manager.get_meta_data()
            for n in list:
                try:
                    if max_dist - distances[n._id] > self._threshold:
                        # Do something here
                        print "*** Node " + str(n._id) + " hit the threshold"
                except KeyError:
                    # Do query here to see if node exists. If it does than node
                    # does not link to origin
                    print "*** Node " + str(n._id) + " may not link to origin"

    def loop(self, limit, sleep=10):
        while 1:
            current_entry = self.source.add_to_queue(limit, sleep)
            found, found_list = self.build_graph(current_entry)
            if found:
                self.events.on_clearing_cache()
                clear_cache(self._port)
                self.analyze_found(found_list)