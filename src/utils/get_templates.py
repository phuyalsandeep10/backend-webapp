import os

from jinja2 import Environment, FileSystemLoader, select_autoescape

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

parent_dir = os.path.dirname(CURRENT_DIR)

templates_dir = os.path.join(parent_dir, "templates")

env = Environment(
    loader=FileSystemLoader(templates_dir),
    autoescape=select_autoescape(["html", "xml"]),
)


async def get_templates(name: str, content: dict):
    template = env.get_template(name)
    return template.render(content)
