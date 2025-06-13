import os

from jinja2 import Environment
from jinja2 import FileSystemLoader

TEMPLATES_FOLDER = os.getenv("TEMPLATES_FOLDER")

env = Environment(loader=FileSystemLoader(TEMPLATES_FOLDER))
