import os
import re

import jinja2
from flask import Flask, redirect, request

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

# webapp2 (Python 2 only, last released 2012) -> Flask
app = Flask(__name__)


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

@app.route('/', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_str("signup-form.html")

    have_error = False
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    verify = request.form.get('verify', '')
    email = request.form.get('email', '')

    params = dict(username = username, email = email)

    if not valid_username(username):
        params['error_username'] = "That's not a valid username."
        have_error = True

    if not valid_password(password):
        params['error_password'] = "That wasn't a valid password."
        have_error = True

    elif password != verify:
        params['error_verify'] = "Your passwords didn't match."
        have_error = True

    if not valid_email(email):
        params['error_email'] = "That's not a valid email."
        have_error = True

    if have_error:
        return render_str('signup-form.html', **params)

    else:
        return redirect('/welcome?username=' + username)

@app.route('/welcome')
def welcome():
    username = request.args.get('username', '')
    if valid_username(username):
        return render_str('index.html', username = username)
    else:
        return redirect('/')
