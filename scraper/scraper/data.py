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

import ConfigParser
import re

from py2neo import authenticate, Graph, Node, Relationship


def get_url(body):
    link = re.findall(r'\[.*\]\s*\(.*\)', body, re.IGNORECASE)[0]
    link = re.findall(r'\(([^\)]+)\)', link)[0].strip()
    if len(re.findall(r'reddit\.com', link, re.IGNORECASE)) > 0:
        return link
    else:
        raise Exception()


def search_replies(comments):
    if comments is None:
        return None
    while len(comments) > 0:
        try:
            return get_url(comments[0].body)
        except:
            comments = comments[0].replies
    return None


def transverse_tree(comments):
    if comments is None:
        return None
    for comment in comments:
        try:
            return get_url(comment.body)
        except:
            try:
                found = transverse_tree(comment.replies)
            except AttributeError:
                continue
            if found:
                return found
    return None


class Access:
    def __init__(self, events, config_file='./config.ini'):
        config = ConfigParser.ConfigParser()
        config.read(config_file)
        authenticate(config.get('db', 'host'), config.get('db', 'username'), config.get('db', 'password'))
        self.graph = Graph()
        self.events = events
        self.port = int(config.get('db', 'com_port'))

    def is_unique_entry(self, entry):
        result = self.graph.find_one('entry', 'clean_url', entry.clean_url)
        if result is None:
            node = Node('entry', clean_url=entry.clean_url, raw_url=entry.raw_url, context=entry.context, searched=0)
            self.graph.create(node)
            return True
        else:
            return result.properties['searched'] == 0

    def mark_searched(self, entry):
        stmt = 'MATCH (found:entry {clean_url: {URL}, searched:0}) SET found.searched = 1'
        self.graph.cypher.execute_one(stmt, URL=entry.clean_url)

    def is_new_node(self, entry):
        if entry.next_entry is None:
            next_id = None
        else:
            next_id = entry.next_entry.id
        result = self.graph.find_one('node', 'self_id', entry.id)
        if result is None:
            self.events.on_creating_node()
            node = Node('node', clean_url=entry.clean_url, raw_url=entry.raw_url, context=entry.context,
                        next_id=next_id, self_id=entry.id, created=entry.created, created_utc=entry.created_utc,
                        source=entry.source_comment, html=entry.html_comment, title=entry.title, user=entry.user,
                        submission_id=entry.submission_id)
            self.graph.create(node)
            return node, False
        else:
            self.events.on_node_exists()
            return result, True

    def get_parents(self, entry):
        stmt = 'MATCH (found:node {next_id: {ID}}) return found'
        results = self.graph.cypher.execute(stmt, ID=entry.id)
        return results.to_subgraph().nodes

    def add_link(self, parent, child):
        if len(list(self.graph.match(start_node=parent, end_node=child, rel_type='linksTo'))) > 0:
            return False
        rel = Relationship(parent, 'linksTo', child)
        self.graph.create_unique(rel)
        return True

    def get_terminus(self, limit=100):
        stmt = 'MATCH (a:node) WHERE NOT (a)-[:linksTo]->() and (not has(a.broken) or a.broken = false) ' + \
               'return a LIMIT {LIM}'
        results = self.graph.cypher.execute(stmt, LIM=limit)
        return results.to_subgraph().nodes

    def get_entry(self, size):
        if size > 0:
            stmt = 'MATCH (found:entry {searched:0}) RETURN found LIMIT {LIM}'
            results = self.graph.cypher.execute(stmt, LIM=size)
        else:
            stmt = 'MATCH (found:entry {searched:0}) RETURN found'
            results = self.graph.cypher.execute(stmt)
        return results.to_subgraph().nodes

    def get_starts(self):
        stmt = 'MATCH (a:node) WHERE NOT ()-[:linksTo]->(a) RETURN a'
        results = self.graph.cypher.execute(stmt)
        return results.to_subgraph().nodes

    def get_next_nodes(self, node):
        stmt = 'MATCH (a:node)-[:linksTo]->(b:node) WHERE id(a) = {ID} RETURN b'
        results = self.graph.cypher.execute(stmt, ID=node._id)
        return results.to_subgraph().nodes

    @staticmethod
    def set_terminus(node):
        node['broken'] = True
        node.push()

    @staticmethod
    def update_parent_next(parent, entry):
        parent['next_id'] = entry.id
        parent.push()


class Entry:
    def __init__(self, url, reddit):
        try:
            self.reddit = reddit
            if len(re.findall(r'.*reddit.com/.*comments/.*', url)) <= 0:
                raise EntryError()
            fixed_url = re.sub(r'(^https?://(www.)?)', 'http://www.', url)
            clean = re.findall(r'.*?(?=\?|/\?|/$|$)', fixed_url)
            context = re.findall(r'(?<=\?context=)\d+', fixed_url)
            self.raw_url = url
            try:
                if len(context) == 1:
                    self.context = int(context[0])
                else:
                    self.context = 0
            except ValueError:
                self.context = 0
            self.clean_url = clean[0] + '/'
            self.full_url = clean[0] + '?context=' + str(self.context)
            self.comment = reddit.get_submission(self.clean_url).comments[0]
            self.source_comment = self.comment.body
            self.html_comment = self.comment.body_html
            self.title = self.comment.submission.title
            if self.comment.author:
                self.user = self.comment.author.name
            else:
                self.user = None
            self.created = self.comment.created
            self.created_utc = self.comment.created_utc
            self.id = self.comment.submission.id + ':' + self.comment.id
            self.submission_id = self.comment.submission.fullname
            self.next_entry = None
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            raise EntryError

    def set_next(self):
        try:
            comment = self.reddit.get_submission(self.full_url).comments
            self.next_entry = Entry(transverse_tree(comment), self.reddit)
        except EntryError:
            pass


class EntryError(Exception):
    pass