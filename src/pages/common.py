from nicegui import app, ui
from utils.security import SecurityService
from core.config import config
from utils.message import MessageService
from datetime import datetime
import logging

class StandardPage():
    """StandardPage
    All page must inherit this page for security issue
    """

    def __init__(self):
        self.header = ui.row().style('background-color: #ebf1fa').props('bordered')
        self.body = ui.row()
        self.footer = ui.row()

        self.init()

    def init(self):
        logging.getLogger().setLevel(logging.DEBUG)
        None

    def logout(self):
        app.storage.user['identity'] = None
        ui.open(config['gui']['login_uri'])

    @ui.refreshable
    def chatArea(target = None) -> None:
        for msg in MessageService().get():
            ui.chat_message(msg['detail'],
                name=msg['message'],
                stamp = msg['stamp'],
                avatar='https://robohash.org/{}'.format(msg['avatar']))

    def build(self, request, roles = None):
        if roles == None:
            # no roles is set so denied
            return False

        session_roles = []
        with ui.header(elevated=True).style('background-color: #c3e3bf').classes('items-center justify-between'):

            logging.debug('Read from session {}'.format(app.storage.user))
    
            if 'identity' in app.storage.user and app.storage.user['identity']:
                logging.debug('Read from session {}'.format(app.storage.user['identity']))
                if 'roles' in app.storage.user['identity']:
                    session_roles = app.storage.user['identity']['roles']
                ui.label('Hi, {} {}'.format(app.storage.user['identity']['username'],session_roles)).style('color: #000000')
                ui.button('LOGOUT', on_click=lambda: self.logout())
            else:
                ui.label('No user identified !!!').style('color: #000000')
                auth_uri = SecurityService().initiateCodeFlow(request = request, scopes = config['security']['scopes'])
                ui.button('LOGIN', on_click=lambda: ui.open(auth_uri))

        allRoleMatch = True

        for role in roles:
            if role not in session_roles:
                allRoleMatch = False

        with self.body:
            ui.label("Role: {}".format(roles))
            ui.separator()
            if not allRoleMatch:
                ui.label('/!\ permission denied')
            else:
                None

        with ui.left_drawer(top_corner=True, bottom_corner=True).style('background-color: #dfe6df'):
            for link in config['gui']['links']:
                ui.link(link['name'],link['route'])
                ui.separator()
            self.chatArea()
    
        with ui.dialog() as dialog, ui.card():
            ui.json_editor({'content': {'json': app.storage.user}},
                    on_select=lambda e: ui.notify(f'Select: {e}'),
                    on_change=lambda e: ui.notify(f'Change: {e}'))
        
        with ui.footer().style('background-color: #c3e3bf'):
            ui.button('Session', on_click=dialog.open)
        
        return allRoleMatch

    # Chat a new message
    def chat(self, message = None, detail = None, avatar = 'info'):
        MessageService().push({
            "message": message,
            "detail": detail,
            'stamp': "{}".format(datetime.now()),
            'avatar': avatar
        })
        self.chatArea.refresh()
