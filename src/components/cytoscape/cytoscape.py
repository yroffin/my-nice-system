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
            "group": ""
        }

        self.data_edge = {
            "label": ""
        }

        # select dialog node
        self.dialog_node = ui.dialog()
        with self.dialog_node, ui.card():
            ui.label('Node')
            label = ui.input(label='Label', placeholder='start typing',
                validation={'Input too long': lambda value: len(value) < 255})
            label.bind_value(self.data_node, target_name = 'label')

            group = ui.input(label='Group', placeholder='start typing',
                validation={'Input too long': lambda value: len(value) < 255})
            group.bind_value(self.data_node, target_name = 'group')

            ui.button('Drop', on_click=lambda: self.dropNode(self.data_node['selected']))
            ui.button('Clone', on_click=lambda: self.cloneNode(self.data_node['selected'], self.graph))
            ui.button('Draw', on_click=lambda: self.start())
            ui.button('Close', on_click=self.dialog_node.close)

        # select dialog node
        self.dialog_edge = ui.dialog()
        with self.dialog_edge, ui.card():
            ui.label('Edge')
            label = ui.input(label='Label', placeholder='start typing',
                validation={'Input too long': lambda value: len(value) < 255})
            label.bind_value(self.data_edge, target_name = 'label')
            ui.button('Drop', on_click=lambda: self.dropEdge(self.data_edge['selected']))
            ui.button('Close', on_click=self.dialog_edge.close)

    def handle_event(self, event):
      if event.args["type"] not in ['mouseout','mouseover']:
        logging.info(json.dumps(event.args))

      if event.args['type'] == 'click' and event.args['target']['type'] == 'node':
        self.data_node['label'] = event.args['target']['data']['label']
        if 'group' in event.args['target']['data']:
           self.data_node['group'] = event.args['target']['data']['group']
        self.data_node['selected'] = event.args['target']
        self.dialog_node.open()

      if event.args['type'] == 'click' and event.args['target']['type'] == 'edge':
        self.data_edge['label'] = event.args['target']['data']['label']
        self.data_edge['selected'] = event.args['target']
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

    def start(self):
      """
      start linking two nodes with edgehandle extention
      """
      self.run_method('start', self.data_node['selected'])
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

    def dropNode(self, data):
      GraphService().dropNode(data["id"])
      self.run_method('dropNode', data)
      self.dialog_node.close()

    def dropEdge(self, data):
      GraphService().dropEdge(data["id"])
      self.run_method('dropEdge', data)
      self.dialog_edge.close()

    def cloneNode(self, data, graph):
       cloned = GraphService().cloneNode(clone = data, id = graph)
       self.run_method('cloneNode', cloned)
       self.dialog_node.close()

    def getNodes(self):
       self.run_method('updateNodePosition')

    def updateNodePosition(self, event):
       for node in event.args:
          GraphService().updateNodePosition(node['data']['id'], node['position']['x'], node['position']['y'])
