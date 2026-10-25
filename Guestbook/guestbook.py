#!/usr/bin/env python3

# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START imports]
import os
from urllib.parse import quote_plus, urlencode

from flask import Flask, redirect, request
from google.appengine.api import users, wrap_wsgi_app
from google.appengine.ext import ndb

import jinja2

# Jinja2 3 has autoescaping built in; the jinja2.ext.autoescape extension is gone.
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    autoescape=True)
# [END imports]

# webapp2 (Python 2 only, last released 2012) -> Flask. wrap_wsgi_app connects it to App Engine's
# bundled services (users, ndb) on the Python 3 runtime; app.yaml turns them on.
app = Flask(__name__)
app.wsgi_app = wrap_wsgi_app(app.wsgi_app)

DEFAULT_GUESTBOOK_NAME = 'default_guestbook'


# We set a parent key on the 'Greetings' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent. However, the write rate should be limited to
# ~1/second.

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity.

    We use guestbook_name as the key.
    """
    return ndb.Key('Guestbook', guestbook_name)


# [START greeting]
class Author(ndb.Model):
    """Sub model for representing an author."""
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)


class Greeting(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    author = ndb.StructuredProperty(Author)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
# [END greeting]


# [START main_page]
# request.values reads the query string and the form, as webapp2's request.get did.
@app.route('/')
def main_page():
    guestbook_name = request.values.get('guestbook_name',
                                        DEFAULT_GUESTBOOK_NAME)
    greetings_query = Greeting.query(
        ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
    greetings = greetings_query.fetch(10)

    user = users.get_current_user()
    if user:
        url = users.create_logout_url(request.url)
        url_linktext = 'Logout'
    else:
        url = users.create_login_url(request.url)
        url_linktext = 'Login'

    template_values = {
        'user': user,
        'greetings': greetings,
        'guestbook_name': quote_plus(guestbook_name),
        'url': url,
        'url_linktext': url_linktext,
    }

    template = JINJA_ENVIRONMENT.get_template('index.html')
    return template.render(template_values)
# [END main_page]


# [START guestbook]
@app.route('/sign', methods=['POST'])
def guestbook():
    # We set the same parent key on the 'Greeting' to ensure each
    # Greeting is in the same entity group. Queries across the
    # single entity group will be consistent. However, the write
    # rate to a single entity group should be limited to
    # ~1/second.
    guestbook_name = request.values.get('guestbook_name',
                                        DEFAULT_GUESTBOOK_NAME)
    greeting = Greeting(parent=guestbook_key(guestbook_name))

    if users.get_current_user():
        greeting.author = Author(
                identity=users.get_current_user().user_id(),
                email=users.get_current_user().email())

    greeting.content = request.values.get('content', '')
    greeting.put()

    query_params = {'guestbook_name': guestbook_name}
    return redirect('/?' + urlencode(query_params))
# [END guestbook]
