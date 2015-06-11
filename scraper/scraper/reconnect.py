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


class Connections:
    def __init__(self, transverse):
        self.t = transverse
        self.data = Access(self.t.events)

    def get_terminus(self):
        return self.data.get_terminus()

    def set_relationship(self, parent_node, child_url):
        entry = Entry(child_url, self.t.reddit)
        entry.set_next()
        node, _ = self.data.is_new_node(entry)
        self.data.update_parent_next(parent_node, entry)
        self.data.add_link(parent_node, node)

    def create_url_relationship(self, parent_url, child_url):
        parent, _ = self.t.data.is_new_node(Entry(parent_url, self.t.reddit))
        child, _ = self.t.data.is_new_node(Entry(child_url, self.t.reddit))
        self.t.data.add_link(parent, child)

    def extend_terminus(self):
        nodes = self.get_terminus()
        for node in nodes:
            if node['next_id']:
                entry = Entry(node['raw_url'], self.t.reddit)
                entry.set_next()
                if entry.next_entry is not None:
                    self.t.build_graph(entry.next_entry)