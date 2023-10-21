import datetime
from peewee import *

from utils.singleton import singleton
import logging
import time
import json

db = SqliteDatabase('.tmp/db.sqlite3')

class BaseModel(Model):
    class Meta:
        database = db

class Graph(BaseModel):
    name = TextField()

class Node(BaseModel):
    label = TextField()
    reference = TextField()
    alias = TextField(null=True)
    group = TextField(null=True)
    x = IntegerField(null=True)
    y = IntegerField(null=True)
    tag = TextField(null=True)
    timestamp = DateTimeField(default=datetime.datetime.now)
    graph = ForeignKeyField(Graph, backref='graphs')

class Edge(BaseModel):
    label = TextField()
    reference = TextField()
    source = ForeignKeyField(Node, backref='node')
    target = ForeignKeyField(Node, backref='node')
    tag = TextField(null=True)
    timestamp = DateTimeField(default=datetime.datetime.now)
    graph = ForeignKeyField(Graph, backref='graphs')

class Style(BaseModel):
    label = TextField(null=True)
    selector = TextField(null=True)
    style = TextField()
    graph = ForeignKeyField(Graph, backref='graphs')

from bs4 import BeautifulSoup

@singleton
class GraphService(object): 

    def graphById(self, id = None):
        return Graph.get(Graph.id == id)

    def graphs(self):
        result = []
        for graph in Graph.select():
            mygraph = {
                    "id": graph.id,
                    "name": graph.name,
                    "nodes": Node.select().where(Node.graph.__eq__(graph.id)).count(),
                    "edges": Edge.select().where(Edge.graph.__eq__(graph.id)).count(),
                    "styles": Style.select().where(Style.graph.__eq__(graph.id)).count()
            }
            result.append(mygraph)
        return result

    def dropNode(self, id):
        # Delete source edge
        deleted = Edge.delete().where(Edge.source == id[1:]).execute()
        logging.info("Drop {} source edge with id {}".format(deleted, id[1:]))
        # Delete target edge
        deleted = Edge.delete().where(Edge.target == id[1:]).execute()
        logging.info("Drop {} target edge with id {}".format(deleted, id[1:]))
        # Delete this node
        deleted = Node.delete().where(Node.id == id[1:]).execute()
        logging.info("Drop {} node with id {}".format(deleted, id[1:]))

    def updateNodePosition(self, id, x, y):
        # Update position
        node = Node.get(Node.id == id[1:])
        node.x = x
        node.y = y
        node.save()

    def cloneNode(self, clone, id):
        mygraph = Graph.get(Graph.id == id)

        reference = None
        if 'id' in clone:
            reference = "{}".format(clone['id'])
        label = None
        if 'label' in clone['data']:
            label = clone['data']['label']
        alias = None
        if 'alias' in clone['data']:
            alias = clone['data']['alias']
        group = None
        if 'group' in clone['data']:
            group = clone['data']['group']
        x = None
        if 'x' in clone['position']:
            x = clone['position']['x'] + 50
        y = None
        if 'y' in clone['position']:
            y = clone['position']['y'] + 50
        tag = None
        if 'tag' in clone['data']:
            tag = clone['data']['tag']

        # create a new node
        node = Node.create(label = label, reference = reference, alias = alias,  group = group,  x = x,  y = y,  tag = tag, graph = mygraph)
        return {
            "id": "n{}".format(node.id),
            "data": {
                "reference": reference,
                "label": label,
                "alias": alias,
                "group": group,
                "tag": tag
            },
            "position":{
                "x": x,
                "y": y
            }
        }

    def dropGraph(self, id):
        # Delete all nodes for this graph
        Node.delete().where(Node.graph.__eq__(id)).execute()
        # Delete all edges for this graph
        Edge.delete().where(Edge.graph.__eq__(id)).execute()
        # Delete style for this graph
        Style.delete().where(Style.graph.__eq__(id)).execute()
        # Delete this graph
        Graph.delete().where(Graph.id.__eq__(id)).execute()

    def createGraph(self, name = 'default'):
        Graph.create(name = name)

    def nodes(self, graph = None):
        result = []
        for node in Node.select().where(Node.graph == graph):
            result.append(
                {
                    "id": node.id,
                    "label": node.label
                }
            )
        return result

    def edges(self, graph = None):
        result = []
        for edge in Edge.select().where(Edge.graph == graph):
            result.append(
                {
                    "id": edge.id,
                    "label": edge.label
                }
            )
        return result

    def graph(self, id: str = None):
        for graph in Graph.select().where(Graph.id == id):
            result = {
                    "id": graph.id,
                    "name": graph.name,
                    "nodes": [],
                    "edges": [],
                    "styles": []
                }
            for node in Node.select().where(Node.graph == id):
                result['nodes'].append({
                    "id": "n{}".format(node.id),
                    "reference": node.reference,
                    "label": node.label,
                    "tag": node.tag,
                    "x": node.x,
                    "y": node.y
                })
            for edge in Edge.select().where(Edge.graph == id):
                result['edges'].append({
                    "id": "e{}".format(edge.id),
                    "reference": edge.reference,
                    "label": edge.label,
                    "tag": edge.tag,
                    "source": "n{}".format(edge.source.id),
                    "target": "n{}".format(edge.target.id),
                    "_source": edge.source.reference,
                    "_target": edge.target.reference,
                })
            for style in Style.select().where(Style.graph == id):
                result['styles'].append({
                    "label": style.label,
                    "selector": style.selector,
                    "style": json.loads(style.style)['css']
                })
        return result

    def loadStyle(self, filename = None, name = None):
        # Reading the data inside the xml
        # file to a variable under the name 
        # data
        with open(filename, 'r') as f:
            data = f.read()
        
        mygraph = Graph.get(Graph.name == name)
        self.loadStyleData(data = data, id = mygraph.id)

    def loadStyleData(self, data = None, id = None):
        start = time.time()
        
        if id:
            mygraph = Graph.select().where(Graph.id == id)
            if len(mygraph) == 1:
                # Delete style for this graph
                Style.delete().where(Style.graph.__eq__(id)).execute()

                # Passing the stored data inside
                # the beautifulsoup parser, storing
                # the returned object 
                Json_data = json.loads(data)
            
                counter=0
                # find all nodes
                for style in Json_data:
                    label = None
                    if 'label' in style:
                        label = style['label']

                    # create a new node
                    style = Style.create(label = label, selector = style['selector'], style = json.dumps(style['style']), graph = mygraph[0])
                    counter += 1

                logging.info('graph {} loaded in {} ms with {} style(s)'.format(mygraph[0].name, (time.time() - start) * 1000, counter))
            else:
                logging.warn('No graph with name {}'.format(id))
        else:
            logging.warn('Name is None')

    def loadGexf(self, filename = None):
        # Reading the data inside the xml
        # file to a variable under the name 
        # data
        with open(filename, 'r') as f:
            data = f.read()
            f.close()
        
        mygraph = Graph.create(name = 'default')
    
        self.loadGexfData(data = data, id = mygraph.id)

    def loadGexfData(self, data = None, id = None):
        start = time.time()
        
        # Passing the stored data inside
        # the beautifulsoup parser, storing
        # the returned object 
        Bs_data = BeautifulSoup(data, "xml")

        mygraph = Graph.get(Graph.id == id)
    
        # Delete all nodes for this graph
        Node.delete().where(Node.graph.__eq__(id)).execute()
        # Delete all edges for this graph
        Edge.delete().where(Edge.graph.__eq__(id)).execute()

        # find all nodes
        for node in Bs_data.find_all('node'):

            reference = None
            if 'id' in node.attrs:
                reference = "{}".format(node.attrs['id'])
            label = None
            if 'label' in node.attrs:
                label = node.attrs['label']
            alias = None
            if 'alias' in node.attrs:
                alias = node.attrs['alias']
            group = None
            if 'group' in node.attrs:
                group = node.attrs['group']
            x = None
            if 'x' in node.attrs:
                x = node.attrs['x']
            y = None
            if 'y' in node.attrs:
                y = node.attrs['y']
            tag = None
            if 'tag' in node.attrs:
                tag = node.attrs['tag']
            
            # create a new node
            node = Node.create(label = label, reference= reference, alias = alias,  group = group,  x = x,  y = y,  tag = tag, graph = mygraph)

        # find all edges
        for edge in Bs_data.find_all('edge'):

            reference = None
            if 'id' in edge.attrs:
                reference = "{}".format(edge.attrs['id'])
            label = None
            if 'label' in edge.attrs:
                label = edge.attrs['label']
            tag = None
            if 'tag' in edge.attrs:
                tag = edge.attrs['tag']
                if len(tag) == 0:
                    tag = None
            source = None
            if 'source' in edge.attrs:
                source = edge.attrs['source']
            target = None
            if 'target' in edge.attrs:
                target = edge.attrs['target']
            
            # find source and target node
            sourceNode= Node.select().where(Node.graph == id).where(Node.reference == source)
            targetNode= Node.select().where(Node.graph == id).where(Node.reference == target)

            # create a new edge
            edge = Edge.create(label = label, reference = reference, source = sourceNode, target = targetNode, tag = tag, graph = mygraph)

        # some statistics      
        nodeCount = len(Node.select().where(Node.graph.__eq__(mygraph.id)))
        edgeCount = len(Edge.select().where(Edge.graph.__eq__(mygraph.id)))

        logging.info('graph {} loaded in {} ms with {} node(s) and {} edge(s)'.format(mygraph.name, (time.time() - start) * 1000, nodeCount, edgeCount))
