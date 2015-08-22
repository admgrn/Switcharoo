import datetime
import time

from flask import Flask, jsonify, render_template, request, Response
from py2neo import authenticate, Graph, Node
from tools.cachemanager import CacheClient
from validate_email import validate_email

app = Flask(__name__)
app.config.from_pyfile('config.ini')

authenticate(app.config['HOST'], app.config['USERNAME'], app.config['PASSWORD'])
graph = Graph()

@app.route('/')
@app.route('/location/<id>')
def index(id=None):
    year = datetime.date.today().year
    copy = '&copy; ' + str(year) + '. RooGraph. All Rights Reserved.'
    return render_template('index.html', copyright=copy)


@app.route('/load_content')
def load_content():
    cache = CacheClient(app.config['PORT'], app.config['AUTH'])
    nodes, relations = cache.get_cache()
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

if __name__ == '__main__':
    app.run()