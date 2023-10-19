from typing import Any, Callable, Optional

from nicegui.element import Element
from nicegui import ui,app

import logging

class Cytoscape(Element, component='cytoscape.js'):

    def __init__(self, title: str, model = None, 
                 width = None,
                 height = None,
                 on_click_node: Optional[Callable[..., Any]] = None, 
                 data_node = None,
                 on_click_edge: Optional[Callable[..., Any]] = None,
                 data_edge = None) -> None:
        super().__init__()

        self.on_click_node = on_click_node
        self.data_node = data_node
        self.on_click_edge = on_click_edge
        self.data_edge = data_edge

        self._props['title'] = title
        self._props['model'] = model
        self._props['nodes'] = model['nodes']
        self._props['edges'] = model['edges']
        ui.add_head_html('<script src="https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.21/lodash.min.js"></script>')
        ui.add_head_html('<script src="https://unpkg.com/cytoscape/dist/cytoscape.min.js"></script>')
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
      
    def handle_event(self, event):

      if event.args['type'] == 'click' and event.args['target']['type'] == 'node':
        if self.on_click_node:
          self.data_node['label'] = event.args['target']['data']['label']
          self.on_click_node()

      if event.args['type'] == 'click' and event.args['target']['type'] == 'edge':
        if self.on_click_edge:
          self.on_click_edge()

    def select(self, data):
       self.run_method('select', data)
