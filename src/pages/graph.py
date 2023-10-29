import base64
import io
from fastapi import Request
from fastapi.responses import StreamingResponse
from components.cytoscape.cytoscape import Cytoscape
from models.graph import GraphService
from pages.common import StandardPage

from nicegui import Tailwind, app, events, ui
from core.config import config
import logging

class GraphsPage(StandardPage):
    """GraphPage
    """

    def init(self):
        self.columns = [
            {'name': 'Name', 'label': 'Label', 'field': 'name'},
            {'name': 'Nodes', 'label': 'Node(s)', 'field': 'nodes'},
            {'name': 'Edges', 'label': 'Edge(s)', 'field': 'edges'},
            {'name': 'Style', 'label': 'Style(s)', 'field': 'styles'},
            {'label': 'Load graph'},
            {'label': 'Load style'},
            {'label': 'Select'},
            {'label': 'Drop'}
        ]

        self.rows = []

    @ui.refreshable
    def tableArea(self) -> None:
        self.rows = []
        for graph in GraphService().graphs():
            self.rows.append({
                "id": graph['id'],
                "name": graph['name'],
                "nodes": graph['nodes'],
                "edges": graph['edges'],
                "styles": graph['styles']
                })

        logging.info(self.rows)
        self.table = ui.table(columns=self.columns, rows=self.rows, row_key='name', pagination={'rowsPerPage': 4, 'sortBy': 'name'})
        self.table.classes('w-full')

        self.table.add_slot('body', r'''
            <q-tr :props="props">
                <q-td v-for="col in props.cols" :key="col.name" :props="props">
                    {{ col.value }}
                </q-td>
                <q-td auto-width>
                    <q-btn color="info" round dense
                        @click="() => $parent.$emit('uploadGraph', props.row)"
                        :icon="'upload'" />
                </q-td>
                <q-td auto-width>
                    <q-btn color="info" round dense
                        @click="() => $parent.$emit('uploadStyle', props.row)"
                        :icon="'upload'" />
                </q-td>
                <q-td auto-width>
                    <q-btn color="info" round dense
                        @click="() => $parent.$emit('select', props.row)"
                        :icon="'lan'" />
                </q-td>
                <q-td auto-width>
                    <q-btn color="info" round dense
                        @click="() => $parent.$emit('drop', props.row)"
                        :icon="'clear'" />
                </q-td>
            </q-tr>
        ''')

        self.table.on('uploadGraph', self.uploadGraph)
        self.table.on('uploadStyle', self.uploadStyle)
        self.table.on('select', self.select)
        self.table.on('drop', self.drop)

    def uploadGraph(self, e: events.GenericEventArguments) -> None:
        self.dialog_upload_graph_args = e.args
        self.dialog_upload_graph.open()

    def uploadStyle(self, e: events.GenericEventArguments) -> None:
        self.dialog_upload_style_args = e.args
        self.dialog_upload_style.open()

    def select(self, e: events.GenericEventArguments) -> None:
        ui.open('/graph/{}'.format(e.args['id']))

    async def drop(self, e: events.GenericEventArguments) -> None:
        result = await self.dialog_confirm
        if result:
            GraphService().dropGraph(e.args['id'])
            self.tableArea.refresh()
    
    def handle_upload_graph(self, e: events.UploadEventArguments):
        text = e.content.read().decode('utf-8')
        mygraph = GraphService().graphById(self.dialog_upload_graph_args['id'])
        GraphService().loadGexfData(data = text, id=mygraph)
        self.dialog_upload_graph.close()
        self.tableArea.refresh()

    def handle_upload_style(self, e: events.UploadEventArguments):
        text = e.content.read().decode('utf-8')
        mygraph = GraphService().graphById(self.dialog_upload_style_args['id'])
        GraphService().loadStyleData(data = text, id=mygraph)
        self.dialog_upload_style.close()
        self.tableArea.refresh()

    def build(self, request):
        # Call inheritance to check roles
        if StandardPage.build(self, request = request, roles = ['ADMIN']):
            with self.body:
                self.chat(message = "Graph", detail = "scan all existing graphs")

                ui.button('New Graph', on_click=lambda: self.newGraph())
                self.tableArea()

                # upload graph dialog
                self.dialog_upload_graph = ui.dialog()
                with self.dialog_upload_graph, ui.card():
                    ui.label('Upload graph')
                    ui.upload(on_upload=self.handle_upload_graph, auto_upload=True).props('accept=.gexf').classes('max-w-full')

                # upload style dialog
                self.dialog_upload_style = ui.dialog()
                with self.dialog_upload_style, ui.card():
                    ui.label('Upload style')
                    ui.upload(on_upload=self.handle_upload_style, auto_upload=True).props('accept=.json').classes('max-w-full')

                # confirmation
                self.dialog_confirm = ui.dialog()
                with self.dialog_confirm, ui.card():
                    ui.label('Are you sure?')
                    with ui.row():
                        ui.button('Yes', on_click=lambda: self.dialog_confirm.submit(True))
                        ui.button('No', on_click=lambda: self.dialog_confirm.submit(False))

    def newGraph(self) -> None:
        GraphService().createGraph()
        self.tableArea.refresh()

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
            {'name': 'action', 'label': 'Select'}
        ]

        self.edgeColumns = [
            {'name': 'id', 'label': 'Id', 'field': 'id', 'sortable': True},
            {'name': 'label', 'label': 'Label', 'field': 'label', 'sortable': True},
            {'name': 'action', 'label': 'Select'}
        ]

    @ui.refreshable
    def tableNode(self) -> None:
        rows = []
        for node in GraphService().nodes(self.graph):
            rows.append({
                "id": "n{}".format(node['id']),
                "label": node['label']
                })

        table = ui.table(columns=self.nodeColumns, rows=rows, row_key='id', pagination={'rowsPerPage': 4, 'sortBy': 'label'})
        table.classes('w-full')

        table.add_slot('body', r'''
            <q-tr :props="props">
                <q-td v-for="col in props.cols" :key="col.name" :props="props">
                    {{ col.value }}
                </q-td>
                <q-td auto-width>
                    <q-btn color="info" round dense
                        @click="() => $parent.$emit('selectNode', props.row)"
                        :icon="'search'" />
                </q-td>
            </q-tr>
        ''')

        table.on('selectNode', self.selectNode)

    def selectNode(self, e: events.GenericEventArguments) -> None:
        self.dialog_search_node.close()
        self.cytoscape.select(e.args['id'])

    @ui.refreshable
    def tableEdge(self) -> None:
        rows = []
        for edge in GraphService().edges(self.graph):
            rows.append({
                "id": "e{}".format(edge['id']),
                "label": edge['label']
                })

        table = ui.table(columns=self.edgeColumns, rows=rows, row_key='id', pagination={'rowsPerPage': 4, 'sortBy': 'label'})
        table.classes('w-full')

        table.add_slot('body', r'''
            <q-tr :props="props">
                <q-td v-for="col in props.cols" :key="col.name" :props="props">
                    {{ col.value }}
                </q-td>
                <q-td auto-width>
                    <q-btn color="info" round dense
                        @click="() => $parent.$emit('selectEdge', props.row)"
                        :icon="'search'" />
                </q-td>
            </q-tr>
        ''')

        table.on('selectEdge', self.selectEdge)

    def selectEdge(self, e: events.GenericEventArguments) -> None:
        self.dialog_search_edge.close()
        self.cytoscape.select(e.args['id'])

    def build(self, request, id):
        # Call inheritance to check roles
        if StandardPage.build(self, request = request, roles = ['ADMIN']):
            with self.body:
                self.chat(message = "Graph", detail = "load graph {}".format(id))

                # store id graph
                self.graph = id

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

                # select dialog statistics
                self.dialog_statistics = ui.dialog()
                with self.dialog_statistics, ui.card() as card:
                    card.style('width: 1024px')
                    card.style('max-width: 1024px')
                    card.style('height: 300px')
                    card.style('max-height: 300px')
                    data = []
                    tags = GraphService().getTags(self.graph)
                    for key in tags:
                        data.append({ "value": tags[key], "name": key })
                    self.echart = ui.echart({
                        "tooltip": {
                            "trigger": 'item'
                        },
                        "legend": {
                            "orient": 'vertical',
                            "left": 'left'
                        },
                        "series": [
                            {
                            "name": 'Tag',
                            "type": 'pie',
                            "radius": '80%',
                            "data": data,
                            "emphasis": {
                                    "itemStyle": {
                                    "shadowBlur": 10,
                                    "shadowOffsetX": 0,
                                    "shadowColor": 'rgba(0, 0, 0, 0.5)'
                                    }
                                }
                            }
                        ]
                    })

                # select dialog parameters
                self.dialog_parameters = ui.dialog()
                with self.dialog_parameters, ui.card():
                    width = ui.input(label='Width', placeholder='start typing')
                    width.bind_value(self.data, target_name="width")
                    height = ui.input(label='Height', placeholder='start typing')
                    height.bind_value(self.data, target_name="height")
                    ui.button('Store', on_click=lambda: self.onStore())

                # select dialog parameters
                self.dialog_png = ui.dialog()
                with self.dialog_png, ui.card():
                    ui.html('<img src="/graph/{}/png">'.format(self.graph))

                self.switch = {
                    "link": False,
                    "group": False
                }

                self.cytoscape = None

                with ui.column():
                    switch_sw = ui.switch('draw mode', on_change=lambda: self.onSwithLink())
                    switch_sw.bind_value(self.switch, target_name="link")
                    switch_grp = ui.switch('group mode', on_change=lambda: self.onSwithGroup())
                    switch_grp.bind_value(self.switch, target_name="group")

                self.myGraph = GraphService().graph(id = id)

                with ui.column():
                    with ui.card():
                        self.cytoscape = Cytoscape('Graph', 
                            width = self.data['width'],
                            height = self.data['height'],
                            graph = self.graph)
                        ui.timer(0.1, lambda: self.refresh(), once = True)

                        with ui.context_menu():
                            ui.menu_item('Parameter(s)', on_click=lambda: self.dialog_parameters.open())
                            ui.separator()
                            ui.menu_item('Search node(s)', on_click=lambda: self.dialog_search_node.open())
                            ui.menu_item('Search edge(s)', on_click=lambda: self.dialog_search_edge.open())
                            ui.menu_item('Fit', on_click=lambda: self.fit())
                            ui.separator()
                            ui.menu_item('Save', on_click=lambda: self.getNodes())
                            ui.menu_item('Reload from server', on_click=lambda: self.refresh())
                            ui.menu_item('Attach PNG to this graph', on_click=lambda: self.png())
                            ui.separator()
                            ui.menu_item('Statistics', on_click=lambda: self.dialog_statistics.open())

    def fit(self):
        if self.cytoscape:
            self.cytoscape.fit()

    def refresh(self):
        self.cytoscape.loadStyle(self.myGraph)
        self.cytoscape.loadNodes(self.myGraph)

        self.echart.update()
        ui.notify('Reload graph from server', close_button='OK')

    def onSwithLink(self):
        if self.cytoscape:
            self.cytoscape.drawMode(self.switch['link'])

    def onSwithGroup(self):
        if self.cytoscape:
            self.cytoscape.groupMode(self.switch['group'])

    def onStore(self):
        app.storage.user['graph_properties'] = self.data
        self.dialog_parameters.close()

    def onClone(self, data = None, graph = None):
        self.cytoscape.cloneNode(data = data, graph = graph)

    def getNodes(self):
        self.cytoscape.getNodes()
        ui.notify('Save current nodes position', close_button='OK')

    async def png(self):
        await self.cytoscape.png()
        ui.notify('Attach PNG to this graph', close_button='OK')
        self.dialog_png.open()

@ui.page('/graph/{id}')
def graphPage(request: Request = None, id: str = None):
    GraphPage().build(request = request, id = id)

@app.get('/graph/{id}/png')
def pngGraph(request: Request = None, id: str = None):
    # exclude data:image/png;base64,
    b64 = str(GraphService().graphById(id).png)[24:]
    imgio = io.BytesIO()
    imgio.write(base64.b64decode(b64))
    imgio.seek(0)
    return StreamingResponse(content=imgio, media_type="image/png")
