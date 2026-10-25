import codecs
import os
import jinja2
from flask import Flask, request

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

# webapp2 (Python 2 only, last released 2012) -> Flask
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def encryption():
    if request.method == 'GET':
        return render_str('index.html')

    text = request.form.get('text', '')
    new_text = ""
    if text:
        # Python 3 has no str.encode('rot13'); the codec lives in codecs.
        new_text = codecs.encode(text, 'rot13')
    return render_str('index.html', text=new_text)
