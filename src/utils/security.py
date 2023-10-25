#!/usr/bin/env python3
"""Security class.
"""

from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware

from nicegui import app, ui, Client

from utils.singleton import singleton

from typing import Optional
from core.config import config
import logging

ldap = {
    "x": {
        "password": "x",
        "roles": ["ADMIN"]
    }
}

unrestricted_page_routes = ['/login']

class AuthMiddleware(BaseHTTPMiddleware):
    """This middleware restricts access to all NiceGUI pages.

    It redirects the user to the login page if they are not authenticated.
    """

    async def dispatch(self, request: Request, call_next):
        # identity session user object handle user identity
        authenticated = app.storage.user.get('identity', None)
        if not authenticated:
            logging.info('User is not authenticated')
            if request.url.path in Client.page_routes.values() and request.url.path not in unrestricted_page_routes:
                logging.info('Redirect to /login with referer {}'.format(request.url.path))
                app.storage.user['referrer_path'] = request.url.path  # remember where the user wanted to go
                return RedirectResponse('/login')
        else:
            if request.url.path in Client.page_routes.values() and request.url.path not in unrestricted_page_routes:
                logging.debug("[CONNECTED] Identity: {} => {}".format(app.storage.user.get('identity'), request.url))
        return await call_next(request)


@ui.page('/login')
def login() -> Optional[RedirectResponse]:
    def try_login() -> None:  # local function to avoid passing username and password as arguments
        if ldap.get(username.value)['password'] == password.value:
            app.storage.user.update({'identity': {'username': username.value, 'roles': ldap.get(username.value)['roles']}})
            ui.open(app.storage.user.get('referrer_path', '/'))  # go back to where the user wanted to go
        else:
            ui.notify('Wrong username or password', color='negative')

    if app.storage.user.get('identity', None):
        return RedirectResponse('/')
    with ui.card().classes('absolute-center'):
        username = ui.input('Username').on('keydown.enter', try_login)
        password = ui.input('Password', password=True, password_toggle_button=True).on('keydown.enter', try_login)
        ui.button('Log in', on_click=try_login)

@singleton
class SecurityService(object): 
    """SecurityService
   handle all security subject : login, logout ...
    """

    def __init__(self):
        None

    def startup(self):
        logging.info('Load middleware')
        app.add_middleware(AuthMiddleware)
        app.add_static_files('/static', 'static')
        ui.run(title = 'Devops GUI', storage_secret=config['gui']['secret'])

    def initiateCodeFlow(self, request = None, scopes = None):
        None

    def acquireToken(self, request: Request = None):
        None
