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
        None

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

                self.myGraph = GraphService().graph(id = id)
                self.cytoscape = Cytoscape('Graph', model = self.myGraph)
                print(self.myGraph)
                ui.separator()
                self.myJson()

@ui.page('/graph/{id}')
def graphPage(request: Request = None, id: str = None):
    GraphPage().build(request = request, id = id)
