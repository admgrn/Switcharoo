import datetime
import math
import random
import time

from beaker.cache import cache_region, cache_regions
from flask import Flask, jsonify, render_template, request, Response
from py2neo import authenticate, Graph, Node
from tools.cachemanager import CacheManager
from validate_email import validate_email

app = Flask(__name__)
app.config.from_pyfile('config.ini')

authenticate(app.config['HOST'], app.config['USERNAME'], app.config['PASSWORD'])

cache_regions.update({
    'short_term': {
        'expire': 60000,
        'type': 'memory'
    }
})

graph = Graph()


def build_key(relation):
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


@cache_region('short_term', 'load_nodes')
def get_data():
    found_paths = graph.cypher.execute('match p=(b:node)<-[:linksTo*]-(a:node) where not ()-[:linksTo]->(a) and ' + \
                                       'not (b)-[:linksTo]->() with p, nodes(p) as items return length(items) ' + \
                                       'as le, extract(n in items|id(n)) as id order by le desc').records
    relations = {}
    nodes = {}
    position = Position()
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
                        relations[build_key(relation)] = relation
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


@app.route('/')
@app.route('/location/<id>')
def index(id=None):
    year = datetime.date.today().year
    copy = '&copy; ' + str(year) + '. RooGraph. All Rights Reserved.'
    return render_template('index.html', copyright=copy)


@app.route('/load_content')
def load_content():
    nodes, relations = get_data()
    return jsonify(nodes=nodes, relations=relations)


@app.route('/get_info/<ident>')
def get_info(ident):
    node = graph.cypher.execute('MATCH (a:node) WHERE id(a) = {ID} RETURN a', ID=int(ident))[0]
    return jsonify(title=node['a']['title'], link=node['a']['raw_url'], html=node['a']['html'],
                   user=node['a']['user'], date=node['a']['created_utc'], id=ident)


@app.route(app.config['CONTACT_URL'], methods=('POST',))
def send_message():
    try:
        email = request.form['email']
        message = request.form['message']
        if not validate_email(email):
            raise Exception()
        if not message.strip():
            raise Exception()
    except:
        resp = 'BAD'
    else:
        resp = 'GOOD'
        node = Node('contact', email=email, message=message, time=time.strftime('%Y-%m-%d %H:%M:%S'), read=0)
        graph.create(node)
    return Response(response=resp, status=200)


@app.route(app.config['SUBMIT_URL'], methods=('POST',))
def submit_roo():
    try:
        link = request.form['link']
        if not link.strip():
            raise Exception()
    except:
        resp = 'BAD'
    else:
        resp = 'GOOD'
        node = Node('submission', link=link, time=time.strftime('%Y-%m-%d %H:%M:%S'), read=0)
        graph.create(node)
    return Response(response=resp, status=200)

CacheManager(get_data).run()

if __name__ == '__main__':
    app.run()