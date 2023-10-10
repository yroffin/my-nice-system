from pages.common import StandardPage

from nicegui import app, ui
from starlette.requests import Request
from core.config import config

class MainPage(StandardPage):
    """MainPage
    """

    def build(self, request):
        # Call inheritance to check roles
        if StandardPage.build(self, request = request, roles = ['READER']):
            with self.body:
                ui.label('home')

        self.chat(message = "Hello", detail = "Main")

@ui.page('/')
def mainPage(request: Request = None):
    MainPage().build(request = request)
