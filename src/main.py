from utils.security import SecurityService
from utils.logger import LoggerService

# Load pages
from pages.main import MainPage

def main():
    LoggerService().startup()
    SecurityService().startup()

if __name__ in {"__main__", "__mp_main__"}:
    main()
