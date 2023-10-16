from pages.common import StandardPage

from nicegui import app, ui
from starlette.requests import Request
from core.config import config

from components.sample import Counter

class MainPage(StandardPage):
    """MainPage
    """

    def build(self, request):
        # Call inheritance to check roles
        if StandardPage.build(self, request = request, roles = ['ADMIN']):
            with self.body:
                ui.label('home')

        self.chat(message = "Hello", detail = "Main")
        
        with self.body:
            with ui.card():
                self.counter = Counter('Clicks', on_change=lambda e: ui.notify(f'The value changed to {e.args}.'))

                ui.button('Reset', on_click=self.onClick).props('small outline')

    async def onClick(self):
        self.counter.reset(1)

@ui.page('/')
def mainPage(request: Request = None):
    MainPage().build(request = request)
