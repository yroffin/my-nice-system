from typing import Any, Callable, Optional

from nicegui.element import Element
from nicegui import ui,app

import json
import asyncio

from models.graph import GraphService

class Cytoscape(Element, component='cytoscape.js'):

    def __init__(
          self,
          title: str,
          model = None, 
          width = None,
          height = None,
          graph = None,
          onClone: Optional[Callable[..., Any]] = None, 
        ):
        super().__init__()

        self.onClone = onClone
        self.graph = graph

        self._props['title'] = title
        self._props['model'] = model
        self._props['nodes'] = model['nodes']
        self._props['edges'] = model['edges']
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
        self.on('nodes', self.nodes)

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
        print(json.dumps(event.args, indent = 2))

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
      print(json.dumps(event.args, indent = 2))

      if event.args['type'] == "ehcomplete":
        GraphService().addEdge(
            source = event.args['addedEdge']['source'],
            target = event.args['addedEdge']['target']
          )
        ui.timer(0.1, lambda: ui.run_javascript('window.location.reload()'), once=True)

    def start(self):
      self.run_method('start', self.data_node['selected'])
      self.dialog_node.close()

    def drawMode(self, value):
      self.run_method('drawMode', value)

    def groupMode(self, value):
      groups = GraphService().getGroups(self.graph)
      self.run_method('groupMode', value, groups)

    def select(self, data):
       self.run_method('select', data)

    def dropNode(self, data):
      GraphService().dropNode(data["id"])
      self.run_method('dropNode', data)

    def dropEdge(self, data):
      GraphService().dropEdge(data["id"])
      self.run_method('dropEdge', data)

    def cloneNode(self, data, graph):
       cloned = self.onClone(data, graph)
       self.run_method('cloneNode', cloned)

    def getNodes(self):
       self.run_method('getNodes')

    def nodes(self, event):
       for node in event.args:
          GraphService().updateNodePosition(node['data']['id'], node['position']['x'], node['position']['y'])
