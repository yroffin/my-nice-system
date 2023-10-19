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
        try:
            app.storage.user['graph_properties']
        except:
            app.storage.user['graph_properties'] = {
                "width": 1024,
                "height": 768
            }
        
        self.data = app.storage.user['graph_properties']

        self.nodeColumns = [
            {'name': 'id', 'label': 'Id', 'field': 'id', 'sortable': True},
            {'name': 'label', 'label': 'Label', 'field': 'label', 'sortable': True},
        ]

        self.edgeColumns = [
            {'name': 'id', 'label': 'Id', 'field': 'id', 'sortable': True},
            {'name': 'label', 'label': 'Label', 'field': 'label', 'sortable': True},
        ]

        self.data_node = {
            "label": ""
        }
        self.data_edge = {
            "label": ""
        }

    @ui.refreshable
    def tableNode(self) -> None:
        rows = []
        for node in GraphService().nodes():
            rows.append({
                "id": "n{}".format(node['id']),
                "label": node['label']
                })

        table = ui.table(columns=self.nodeColumns, rows=rows, row_key='id', pagination={'rowsPerPage': 4, 'sortBy': 'label'}, selection="single", on_select=lambda: self.select(table))
        table.classes('w-full')

    @ui.refreshable
    def tableEdge(self) -> None:
        rows = []
        for edge in GraphService().edges():
            rows.append({
                "id": "e{}".format(edge['id']),
                "label": edge['label']
                })

        table = ui.table(columns=self.edgeColumns, rows=rows, row_key='id', pagination={'rowsPerPage': 4, 'sortBy': 'label'}, selection="single", on_select=lambda: self.select(table))
        table.classes('w-full')

    async def select(self, table):
        if len(table.selected) != 0:
            self.cytoscape.select(table.selected[0]['id'])

    def build(self, request, id):
        # Call inheritance to check roles
        if StandardPage.build(self, request = request, roles = ['ADMIN']):
            with self.body:
                self.chat(message = "Graph", detail = "load graph {}".format(id))

                # select dialog node
                self.dialog_search_node = ui.dialog()
                with self.dialog_search_node, ui.card():
                    ui.label('Search')
                    self.tableNode()

                # select dialog edge
                self.dialog_search_edge = ui.dialog()
                with self.dialog_search_edge, ui.card():
                    ui.label('Search')
                    self.tableEdge()

                # select dialog parameters
                self.dialog_parameters = ui.dialog()
                with self.dialog_parameters, ui.card():
                    width = ui.input(label='Width', placeholder='start typing')
                    width.bind_value(self.data, target_name="width")
                    height = ui.input(label='Height', placeholder='start typing')
                    height.bind_value(self.data, target_name="height")
                    ui.button('Store', on_click=lambda: self.onStore())

                ui.button('Store', on_click=lambda: self.dialog_parameters.open())
                ui.button('Search node(s)', on_click=lambda: self.dialog_search_node.open())
                ui.button('Search edge(s)', on_click=lambda: self.dialog_search_edge.open())

                # select dialog node
                self.dialog_node = ui.dialog()
                with self.dialog_node, ui.card():
                    ui.label('Node')
                    label = ui.input(label='Label', placeholder='start typing',
                        validation={'Input too long': lambda value: len(value) < 255})
                    label.bind_value(self.data_node, target_name = 'label')
                    ui.button('Close', on_click=self.dialog_node.close)

                # select dialog node
                self.dialog_edge = ui.dialog()
                with self.dialog_edge as dialog, ui.card():
                    ui.label('Edge')
                    label = ui.input(label='Label', placeholder='start typing',
                        validation={'Input too long': lambda value: len(value) < 255})
                    label.bind_value(self.data_edge, target_name = 'label')
                    ui.button('Close', on_click=dialog.close)

                self.myGraph = GraphService().graph(id = id)

                with ui.card():
                    self.cytoscape = Cytoscape('Graph', 
                        model = self.myGraph, 
                        width = self.data['width'],
                        height = self.data['height'],
                        on_click_node=self.dialog_node.open, 
                        data_node = self.data_node,
                        on_click_edge=self.dialog_edge.open, 
                        data_edge = self.data_edge)
    
    def onStore(self):
        app.storage.user['graph_properties'] = self.data
        self.dialog_parameters.close()

@ui.page('/graph/{id}')
def graphPage(request: Request = None, id: str = None):
    GraphPage().build(request = request, id = id)
