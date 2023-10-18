from fastapi import Request
from components.cytoscape.cytoscape import Cytoscape
from models.graph import GraphService
from pages.common import StandardPage

from nicegui import app, ui
from core.config import config
import logging

class GraphsPage(StandardPage):
    """GraphPage
    """

    def init(self):
        self.columns = [
            {'action': '...', 'name': 'Name', 'label': 'Label', 'field': 'name'}
        ]

        self.rows = []

    @ui.refreshable
    def table(self) -> None:
        self.rows = []
        for graph in GraphService().graphs():
            self.rows.append({
                "id": graph['id'],
                "name": graph['name']
                })

        logging.info(self.rows)
        self.table = ui.table(columns=self.columns, rows=self.rows, row_key='name', pagination={'rowsPerPage': 4, 'sortBy': 'name'}, selection="single", on_select=lambda: self.alert())
        self.table.classes('w-full')

    def build(self, request):
        # Call inheritance to check roles
        if StandardPage.build(self, request = request, roles = ['ADMIN']):
            with self.body:

                self.chat(message = "Graph", detail = "scan all existing graphs")

                self.table()

                # load button
                self.button = ui.button('Load', on_click=lambda: self.onClick())
                self.button.disable()

    async def alert(self):
        if len(self.table.selected) == 0:
            self.button.disable()
        else:
            self.button.enable()

    async def onClick(self):
        ui.open('/graph/{}'.format(self.table.selected[0]['id']))

@ui.page('/graphs')
def graphsPage(request: Request = None):
    GraphsPage().build(request = request)

class GraphPage(StandardPage):
    """GraphPage
    """

    def init(self):
        self.data_node = {
            "label": ""
        }
        self.data_edge = {
            "label": ""
        }

    @ui.refreshable
    def myJson(self) -> None:
        ui.json_editor({'content': {'json': self.myGraph}},
                on_select=lambda e: ui.notify(f'Select: {e}'),
                on_change=lambda e: ui.notify(f'Change: {e}'))

    def build(self, request, id):
        # Call inheritance to check roles
        if StandardPage.build(self, request = request, roles = ['ADMIN']):
            with self.body:
                self.chat(message = "Graph", detail = "load graph {}".format(id))

                # select dialog node
                self.dialog_node = ui.dialog()
                with self.dialog_node as dialog, ui.card():
                    ui.label('Node')
                    label = ui.input(label='Label', placeholder='start typing',
                        validation={'Input too long': lambda value: len(value) < 255})
                    label.bind_value(self.data_node, target_name = 'label')
                    ui.button('Close', on_click=dialog.close)

                # select dialog node
                self.dialog_edge = ui.dialog()
                with self.dialog_edge as dialog, ui.card():
                    ui.label('Edge')
                    label = ui.input(label='Label', placeholder='start typing',
                        validation={'Input too long': lambda value: len(value) < 255})
                    label.bind_value(self.data_edge, target_name = 'label')
                    ui.button('Close', on_click=dialog.close)

                self.myGraph = GraphService().graph(id = id)
                self.cytoscape = Cytoscape('Graph', 
                                           model = self.myGraph, 
                                           on_click_node=self.dialog_node.open, 
                                           data_node = self.data_node,
                                           on_click_edge=self.dialog_edge.open, 
                                           data_edge = self.data_edge)
                ui.separator()
                self.myJson()

@ui.page('/graph/{id}')
def graphPage(request: Request = None, id: str = None):
    GraphPage().build(request = request, id = id)
