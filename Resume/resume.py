import os
import jinja2
from flask import Flask

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

# webapp2 (Python 2 only, last released 2012) -> Flask
app = Flask(__name__)

@app.route('/')
def resume():
    return render_str('index.html')
