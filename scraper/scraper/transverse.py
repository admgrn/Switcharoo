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
from source import Source


class Transverse:
    def __init__(self, events):
        self.reddit = praw.Reddit(user_agent='Switcharoo Cartographer v.0.1.1')
        self.events = events
        self.queue = None
        self.data = Access(self.events)
        self.source = Source(self)
        self._should_stop = False

    def init_queue(self):
        if self.queue is None:
            self.queue = EntryQueue(self)

    def build_graph(self, current_entry):
        entry_point = True
        stop = False
        found = False
        while current_entry is not None and not stop:
            current_entry.set_next()
            if current_entry.next_entry is None and entry_point:
                self.source.mark_searched(current_entry)
                return
            entry_point = False
            # Check if item is already in graph
            node, stop = self.data.is_new_node(current_entry)
            if node is None:
                self.source.mark_searched(current_entry)
                return
            # New node
            if not stop:
                found = True
            parents = self.data.get_parents(current_entry)
            for parent in parents:
                created = self.data.add_link(parent, node)
                if created:
                    found = True
            self.source.mark_searched(current_entry)
            current_entry = current_entry.next_entry
        return found

    def loop(self, limit, sleep=10):
        while 1:
            current_entry = self.source.add_to_queue(limit, sleep)
            if self.build_graph(current_entry):
                self.events.on_clearing_cache()
                clear_cache()