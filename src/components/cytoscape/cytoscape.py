from typing import Any, Callable, Optional

from nicegui.element import Element
from nicegui import ui,app

import json
import logging

from models.graph import GraphService

class Cytoscape(Element, component='cytoscape.js'):
    """
    This component is based on https://js.cytoscape.org/
    """

    def __init__(
          self,
          title: str,
          width = None,
          height = None,
          graph = None
        ):
        super().__init__()

        # store graph id
        self.graph = graph

        self._props['title'] = title
        ui.add_head_html('<script src="https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.21/lodash.min.js"></script>')
        ui.add_head_html('<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.7.1/jquery.min.js" integrity="sha512-v2CJ7UaYy4JwqLDIrZUI/4hqeoQieOmAZNXBeQyjo21dadnwR+8ZaIJVT8EE2iyI61OV8e6M8PP2/4hpQINQ/g==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>')
        ui.add_head_html('<script src="https://unpkg.com/cytoscape/dist/cytoscape.min.js"></script>')
        ui.add_head_html('<script src="/static/cytoscape-edgehandles.js"></script>')
        ui.add_head_html('<script src="/static/cytoscape-snap-to-grid.js"></script>')
        ui.add_head_html('<script src="/static/cytoscape-automove.js"></script>')
        ui.add_head_html(
            f'''
<style>
      .cy {{
        width: {width}px;
        height: {height}px;
        z-index: 999;
      }}
</style>
            ''')

        self.on('event', self.handle_event)
        self.on('edgehandle', self.handle_eventedgehandle)
        self.on('updateNodePosition', self.updateNodePosition)

        self.data_node = {
            "label": "",
            "reference": "",
            "alias": "",
            "group": "",
            "tag": ""
        }
        self.data_node_id = None

        self.data_edge = {
            "label": "",
            "reference": "",
        }
        self.data_edge_id = None

        # select dialog node
        self.dialog_node = ui.dialog()
        with self.dialog_node, ui.card() as card:
            card.style('width: 15%')
            card.style('max-width: 15%')
            card.style('height: 85%')
            card.style('max-height: 85%')

            ui.label('Node')

            for field in ['label','reference','alias','group','tag']:
              label = ui.input(label=field, placeholder='start typing value for {}'.format(field)).style('width: 100%')
              label.bind_value(self.data_node, target_name = field)
            
            ui.separator()

            ui.button('Alias', on_click=lambda: self.findAlias(self.data_node_id))
            ui.button('Drop', on_click=lambda: self.dropNode(self.data_node_id))
            ui.button('Clone', on_click=lambda: self.cloneNode(
              {
                "label": self.data_node["label"],
                "reference": self.data_node["reference"],
                "alias": self.data_node["alias"],
                "group": self.data_node["group"],
                "tag": self.data_node["tag"],
                "x": self.data_node["x"] + 50,
                "y": self.data_node["y"] + 50
              }, self.graph))
            ui.button('Draw', on_click=lambda: self.start())
            ui.button('Save', on_click=lambda: self.saveNode())

        # select dialog node
        self.dialog_edge = ui.dialog()
        with self.dialog_edge, ui.card():
            ui.label('Edge')

            for field in ['label','reference']:
              label = ui.input(label=field, placeholder='start typing value for {}'.format(field)).style('width: 100%')
              label.bind_value(self.data_edge, target_name = field)

            ui.button('Drop', on_click=lambda: self.dropEdge(self.data_edge_id))

    def handle_event(self, event):
      if event.args["type"] not in ['mouseout','mouseover']:
        logging.info(json.dumps(event.args))

      if event.args['type'] == 'click' and event.args['target']['type'] == 'node':
        for field in ['label','reference','alias','group','tag']:
          if field in event.args['target']['data']:
            self.data_node[field] = event.args['target']['data'][field]
        for field in ['x','y']:
          if field in event.args['target']['position']:
            self.data_node[field] = event.args['target']['position'][field]
        self.data_node_id = event.args['target']['id']
        self.dialog_node.open()

      if event.args['type'] == 'click' and event.args['target']['type'] == 'edge':
        for field in ['label','reference']:
          if field in event.args['target']['data']:
            self.data_edge[field] = event.args['target']['data'][field]

        self.data_edge_id = event.args['target']['id']
        self.dialog_edge.open()

    def handle_eventedgehandle(self, event):
      """
      Handle edgehandle events
      Cf. https://github.com/cytoscape/cytoscape.js-edgehandles
      """
      logging.info(json.dumps(event.args))

      if event.args['type'] == "ehcomplete":
        GraphService().addEdge(
            source = event.args['addedEdge']['source'],
            target = event.args['addedEdge']['target']
          )
        graph = GraphService().graph(id = self.graph)
        self.run_method("loadNodes", graph)

    def loadNodes(self, graph):
      """
      reload graph (nodes and edges)
      """
      self.run_method("loadNodes", graph)

    def loadStyle(self, graph):
      self.run_method("loadStyle", graph)

    def saveNode(self):
      """
      update node fields
      """
      GraphService().updateNode(id = self.data_node_id, data = {
              "label": self.data_node["label"],
              "reference": self.data_node["reference"],
              "alias": self.data_node["alias"],
              "group": self.data_node["group"],
              "tag": self.data_node["tag"]
            })
      graph = GraphService().graph(id = self.graph)
      self.run_method("loadNodes", graph)
      for key in self.data_node:
        self.data_node[key] = None
      self.dialog_node.close()

    def start(self):
      """
      start linking two nodes with edgehandle extention
      """
      self.run_method('start', self.data_node_id)
      self.dialog_node.close()

    def drawMode(self, value):
      """
      switch draw mode with edgehandle extention
      """
      self.run_method('drawMode', value)

    def groupMode(self, value):
      """
      activate/disable group mode
      Cf. https://github.com/cytoscape/cytoscape.js-automove/blob/master/cytoscape-automove.js
      """
      groups = GraphService().getGroups(self.graph)
      self.run_method('groupMode', value, groups)

    def select(self, data):
       """
       Select a single node onto current raph
       """
       self.run_method('select', data)

    def findAlias(self, id):
      selected = GraphService().getAlias(id)
      self.select(selected)

    def dropNode(self, id):
      GraphService().dropNode(id)
      self.run_method('dropNode', id)
      self.dialog_node.close()

    def dropEdge(self, id):
      GraphService().dropEdge(id)
      self.run_method('dropEdge', id)
      self.dialog_edge.close()

    def cloneNode(self, data, graph):
      cloned = GraphService().cloneNode(clone = data, id = graph)
      self.run_method('cloneNode', cloned)
      self.dialog_node.close()

    def getNodes(self):
      self.run_method('updateNodePosition')

    def fit(self):
      self.run_method('fit')

    async def png(self):
      png = await self.run_method('png')
      GraphService().updatePngToGraphById(self.graph, png)

    def updateNodePosition(self, event):
       for node in event.args:
          GraphService().updateNodePosition(node['data']['id'], node['position']['x'], node['position']['y'])
