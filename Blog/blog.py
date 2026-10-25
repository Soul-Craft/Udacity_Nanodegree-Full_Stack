# Building a Blog

# Imports
import os
import jinja2
from flask import Flask, redirect, request
from google.appengine.api import wrap_wsgi_app
from google.appengine.ext import db

# Setting Up Jinja Templates
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

# Setting up the Web App: webapp2 (Python 2 only, last released 2012) -> Flask. wrap_wsgi_app
# connects it to App Engine's bundled services (the db datastore API); app.yaml turns them on.
app = Flask(__name__)
app.wsgi_app = wrap_wsgi_app(app.wsgi_app)

# Front Page of the Blog
@app.route('/')
def front():
    query = """
            SELECT *
            FROM Blog
            ORDER BY created DESC
            LIMIT 10;
            """
    blogs = db.GqlQuery(query)
    return render_str('index.html', blogs = blogs)

# Viewing an Individual Blog Post
@app.route('/<int:blog_id>')
def blog_post(blog_id):
    key = db.Key.from_path('Blog', int(blog_id), parent = blog_key())
    blog = db.get(key)
    return render_str('blog_post.html', blog = blog)

# Adding a Blog Post
@app.route('/newpost', methods=['GET', 'POST'])
def new_post():
    if request.method == 'GET':
        return render_str("new_post.html")

    subject = request.form.get('subject', '')
    content = request.form.get('content', '')

    if subject and content:
        b = Blog(parent = blog_key(), subject = subject, content = content)
        b.put()
        return redirect('/%s' % str(b.key().id()))
    else:
        error = "You need to enter both a subject and content"
        return render_str('new_post.html', subject = subject, content = content, error = error)

# Setting Up the Blog Database
def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Blog(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str('index.html', blog = self)
