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
    reference = TextField(unique=True)
    alias = TextField(null=True)
    group = TextField(null=True)
    x = IntegerField(null=True)
    y = IntegerField(null=True)
    tag = TextField(null=True)
    timestamp = DateTimeField(default=datetime.datetime.now)
    graph = ForeignKeyField(Graph, backref='graphs')

class Edge(BaseModel):
    label = TextField()
    reference = TextField(unique=True)
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
    
    def graphs(self):
        result = []
        for graph in Graph.select():
            result.append(
                {
                    "id": graph.id,
                    "name": graph.name
                }
            )
        return result

    def nodes(self):
        result = []
        for node in Node.select():
            result.append(
                {
                    "id": node.id,
                    "label": node.label
                }
            )
        return result

    def edges(self):
        result = []
        for edge in Edge.select():
            result.append(
                {
                    "id": edge.id,
                    "label": edge.label
                }
            )
        return result

    def graph(self, id: str = None):
        for graph in Graph.select().where(Graph.id.__eq__(id)):
            result = {
                    "id": graph.id,
                    "name": graph.name,
                    "nodes": [],
                    "edges": [],
                    "styles": []
                }
            for node in Node.select().where(Node.graph.__eq__(id)):
                result['nodes'].append({
                    "id": "n{}".format(node.id),
                    "reference": node.reference,
                    "label": node.label,
                    "tag": node.tag,
                    "x": node.x,
                    "y": node.y
                })
            for edge in Edge.select().where(Edge.graph.__eq__(id)):
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
            for style in Style.select().where(Style.graph.__eq__(id)):
                result['styles'].append({
                    "label": style.label,
                    "selector": style.selector,
                    "style": json.loads(style.style)['css']
                })
        return result

    def loadStyle(self, filename = None, name = None):
        start = time.time()

        # Reading the data inside the xml
        # file to a variable under the name 
        # data
        with open(filename, 'r') as f:
            data = f.read()
        
        if name:
            mygraph = Graph.select().where(Graph.name.__eq__(name))
            if len(mygraph) == 1:
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
                logging.warn('No graph with name {}'.format(name))
        else:
            logging.warn('Name is None')

    def loadGexf(self, filename = None):
        start = time.time()

        # Reading the data inside the xml
        # file to a variable under the name 
        # data
        with open(filename, 'r') as f:
            data = f.read()
        
        # Passing the stored data inside
        # the beautifulsoup parser, storing
        # the returned object 
        Bs_data = BeautifulSoup(data, "xml")

        mygraph = Graph.create(name = 'default')
    
        # find all nodes
        for node in Bs_data.find_all('node'):

            reference = None
            if 'id' in node.attrs:
                reference = node.attrs['id']
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
                reference = edge.attrs['id']
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
            sourceNode= Node.select().where(Node.reference.__eq__(source))
            targetNode= Node.select().where(Node.reference.__eq__(target))

            # create a new edge
            edge = Edge.create(label = label, reference = reference, source = sourceNode, target = targetNode, tag = tag, graph = mygraph)

        # some statistics      
        nodeCount = len(Node.select().where(Node.graph.__eq__(mygraph.id)))
        edgeCount = len(Edge.select().where(Edge.graph.__eq__(mygraph.id)))

        logging.info('graph {} loaded in {} ms with {} node(s) and {} edge(s)'.format(mygraph.name, (time.time() - start) * 1000, nodeCount, edgeCount))
