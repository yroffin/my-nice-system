from typing import Callable, Optional

from nicegui.element import Element
from nicegui import ui,app

import logging

class Counter(Element, component='sample.js', exposed_libraries=['sampleMylib.js']):

    def __init__(self, title: str, *, on_change: Optional[Callable] = None) -> None:
        super().__init__()
        self._props['title'] = title
        self.on('change', on_change)
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

    def reset(self, value) -> None:
        self.run_method('reset', value)