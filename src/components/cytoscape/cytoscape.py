from typing import Callable, Optional

from nicegui.element import Element
from nicegui import ui,app

import logging

class Cytoscape(Element, component='cytoscape.js'):

    def __init__(self, title: str, model = None) -> None:
        super().__init__()
        self._props['title'] = title
        self._props['model'] = model
        self._props['nodes'] = model['nodes']
        self._props['edges'] = model['edges']
        ui.add_head_html('<script src="https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.21/lodash.min.js"></script>')
        ui.add_head_html('<script src="https://unpkg.com/cytoscape/dist/cytoscape.min.js"></script>')
        ui.add_head_html(
            '''
<style>
      body {
        font-family: helvetica;
        font-size: 14px;
      }

      .cy {
        width: 500px;
        height: 500px;
        z-index: 999;
      }

      h1 {
        opacity: 0.5;
        font-size: 1em;
      }

      button {
        margin-right: 10px;
      }
</style>
            ''')

