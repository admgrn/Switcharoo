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
import praw

from scraper.data import Access
from scraper.events import EventsBase

r = praw.Reddit(user_agent='test')

events = EventsBase()
data = Access(events)

# Submission ID
nodes = data.graph.cypher.execute('MATCH (a:node) RETURN a').to_subgraph().nodes
for node in nodes:
    print node['clean_url']
    node['clean_url'] = node['clean_url'].replace('http://', 'https://', 1)
    print "  => " + node['clean_url']
    node.push()

