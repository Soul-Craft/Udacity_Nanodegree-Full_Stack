import os
import jinja2
from flask import Flask, redirect, request

from google.appengine.api import wrap_wsgi_app
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

# webapp2 (Python 2 only, last released 2012) -> Flask. wrap_wsgi_app connects it to App Engine's
# bundled services (the db datastore API) on the Python 3 runtime; app.yaml turns them on.
app = Flask(__name__)
app.wsgi_app = wrap_wsgi_app(app.wsgi_app)

class Art(db.Model):
    title = db.StringProperty(required = True)
    art = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

def render_front(title = "", art = "", error = ""):
    arts = db.GqlQuery("SELECT * FROM Art ORDER BY created DESC")
    return render_str('ascii.html', title=title, art=art, error=error,arts=arts)

@app.route('/', methods=['GET', 'POST'])
def ascii_art():
    if request.method == 'GET':
        return render_front()

    title = request.form.get('title', '')
    art = request.form.get('art', '')

    if title and art:
        a = Art(title = title, art = art)
        a.put()

        return redirect('/')

    else:
        error = 'we need both a title and some artwork!'
        return render_front(title = title, art = art, error = error)
