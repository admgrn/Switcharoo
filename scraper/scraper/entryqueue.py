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

from data import Access, Entry
from Queue import Queue


class EntryQueue(Queue):
    def __init__(self, transverse, maxsize=0):
        self.reddit = transverse.reddit
        self.events = transverse.events
        Queue.__init__(self, maxsize)

    def _init(self, maxsize):
        Queue._init(self, maxsize)
        nodes = Access(self.events).get_entry(maxsize)
        for node in nodes:
            try:
                self.queue.append(Entry(node['raw_url'], self.reddit))
            except:
                # TODO Remove old entry from DB
                pass

    def _put(self, url):
        entry = Entry(url, self.reddit)
        if self._is_unique(entry):
            self.events.on_adding_to_queue(url)
            self.queue.append(entry)
        else:
            self.events.on_not_adding_to_queue(url)

    def _get(self):
        return self.queue.popleft()

    def _is_unique(self, entry):
        # TODO Logic here to determine if new url found
        if entry not in self.queue:
            return Access(self.events).is_unique_entry(entry)
        else:
            return False