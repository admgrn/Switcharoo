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

import ConfigParser
import math
import random

from py2neo import authenticate, Graph

class GraphBuilder:
    def __init__(self, config_file):
        config = ConfigParser.ConfigParser()
        config.read(config_file)
        authenticate(config.get('db', 'host'), config.get('db', 'username'), config.get('db', 'password'))
        self._graph = Graph()
        self.port = int(config.get('local', 'port'))
        self.auth = config.get('local', 'auth')

    @staticmethod
    def _build_key(relation):
        return str(relation['from']) + ':' + str(relation['to'])

    class Position:
        def __init__(self):
            self._dist = 3000
            self.x = 0
            self.y = 0
            self.d = self._dist
            self.r = 0

        def get_node(self):
            return {'x': self.x, 'y': self.y, 'd': self.d, 'r': self.r}

        def update_position(self, rand):
            if rand:
                rand_amount = self._dist / 3
            else:
                rand_amount = 2
            rand_x = random.randint(-1 * rand_amount, rand_amount)
            rand_y = random.randint(-1 * rand_amount, rand_amount)
            rotation = (300 * 360) / (self.d * math.pi)
            distance = self._dist * (rotation / 360)
            self.d += distance
            self.r = (self.r + rotation) % 360
            x = (math.cos(math.radians(rotation)) * self.x + math.sin(math.radians(rotation)) * self.y) + rand_x
            y = (-math.sin(math.radians(rotation)) * self.x + math.cos(math.radians(rotation)) * self.y) + rand_y
            self.x = int(x + distance * -math.cos(math.radians(self.r)))
            self.y = int(y + distance * math.sin(math.radians(self.r)))

        def set_position(self, node):
            self.x = node['x']
            self.y = node['y']
            self.d = node['d']
            self.r = node['r']

    def get_data(self):
        found_paths = self._graph.cypher.execute('match p=(b:node)<-[:linksTo*]-(a:node) where not ()-[:linksTo]->(a) and '
                                            'not (b)-[:linksTo]->() with p, nodes(p) as items return length(items) '
                                           'as le, extract(n in items|id(n)) as id order by le desc').records
        relations = {}
        nodes = {}
        position = self.Position()
        if len(found_paths):
            for path in found_paths:
                ids = path['id']
                path_size = path['le']
                if path_size > 0:
                    relation = {}
                    prev_node = None
                    for i in range(0, path_size):
                        if i > 0 or (path_size > 1 and i == path_size - 1):
                            relation['from'] = ids[i]
                            relations[self._build_key(relation)] = relation
                            relation = {}
                        relation['to'] = ids[i]
                        if ids[i] not in nodes:
                            if prev_node:
                                position.set_position(nodes[prev_node])
                            if i > 0:
                                position.update_position(prev_node)
                            node = position.get_node()
                            node['id'] = ids[i]
                            node['title'] = str(i)
                            nodes[ids[i]] = node
                            prev_node = None
                        else:
                            prev_node = ids[i]
        node_list = [{'id': x['id'], 'label': x['title'], 'x': x['x'], 'y': x['y']} for _, x in nodes.iteritems()]
        rel_list = [{'from': x['from'], 'to': x['to']} for _, x in relations.iteritems()]
        return node_list, rel_list