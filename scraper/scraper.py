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

from scraper.console import ConsoleManager
from scraper.events import EventsBase
from scraper.reconnect import Connections
from scraper.transverse import Transverse

events = EventsBase()
manager = ConsoleManager()
transverse = Transverse(events)
connection = Connections(transverse)


@manager.register("extend_all", "usage: extend_all")
def link_terminus():
    while 1:
        nodes = connection.get_terminus()
        if len(nodes) <= 0:
            break
        for node in nodes:
            print node['raw_url']
            link = raw_input('  Enter link [() for broken]: ').strip()
            if link == '()':
                transverse.data.set_terminus(node)
                continue
            connection.set_relationship(node, link)
        connection.extend_terminus()


@manager.register("create_rel", "usage: create_rel")
def create_relationship():
    parent = raw_input('  Enter parent URL: ').strip()
    child = raw_input('  Enter child URL: ').strip()
    try:
        connection.create_url_relationship(parent, child)
        print "  Success"
    except:
        print "  An error occurred. Please try again."


@manager.register("scrape", "usage: scrape <limit>")
def scrape(limit=10):
    limit = int(limit)
    transverse.loop(limit)


@manager.help
def helper(methods):
    for method in methods:
        print "\n  " + method[0]
        print "     - " + method[1]
    print "\n  exit"
    print "     - usage: exit\n"


manager.console_loop()