import datetime
from peewee import *

from utils.singleton import singleton
import logging
import time

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

    def graph(self, id: str = None):
        for graph in Graph.select().where(Graph.id.__eq__(id)):
            result = {
                    "id": graph.id,
                    "name": graph.name,
                    "nodes": [],
                    "edges": []
                }
            for node in Node.select().where(Node.graph.__eq__(id)):
                result['nodes'].append({
                    "id": node.id,
                    "label": node.label
                })
            for edge in Edge.select().where(Edge.graph.__eq__(id)):
                result['edges'].append({
                    "id": edge.id,
                    "label": edge.label,
                    "source": edge.source.id,
                    "target": edge.target.id,
                })
        return result

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
