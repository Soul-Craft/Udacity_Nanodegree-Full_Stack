## Forum - a buggy web forum server backed by a good database

# Imports
from forumdb import get_all_posts, add_post
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server
from wsgiref import util
import bleach
import os

# HTML template for the forum page
HTML_WRAP = '''\
<!DOCTYPE html>
<html>
  <head>
    <title>DB Forum</title>
    <style>
      h1, form { text-align: center; }
      textarea { width: 400px; height: 100px; }
      div.post { border: 1px solid #999;
                 padding: 10px 10px;
		 margin: 10px 20%%; }
      hr.postbound { width: 50%%; }
      em.date { color: #999 }
    </style>
  </head>
  <body>
    <h1>DB Forum</h1>
    <form method=post action="/post">
      <div><textarea id="content" name="content"></textarea></div>
      <div><button id="go" type="submit">Post message</button></div>
    </form>
    <!-- post content will go here -->
%s
  </body>
</html>
'''

# HTML template for an individual comment
POST = '''\
    <div class=post><em class=date>%(time)s</em><br>%(content)s</div>
'''

## Request handler for main page
def View(env, resp):
    '''View is the 'main page' of the forum.

    It displays the submission form and the previously posted messages.
    '''
    # get posts from database
    posts = get_all_posts()
    # send results
    headers = [('Content-type', 'text/html; charset=utf-8')]
    resp('200 OK', headers)
    # Python 3 WSGI bodies are bytes
    return [(HTML_WRAP % ''.join(POST % p for p in posts)).encode()]

## Request handler for posting - inserts to database
def Post(env, resp):
    '''Post handles a submission of the forum's form.
  
    The message the user posted is saved in the database, then it sends a 302
    Redirect back to the main page so the user can see their new post.
    '''
    # Get post content
    input = env['wsgi.input']
    length = int(env.get('CONTENT_LENGTH') or 0)
    # If length is zero, post is empty - don't save it.
    if length > 0:
        postdata = input.read(length).decode()
        fields = parse_qs(postdata)
        content = fields['content'][0]
        # If the post is just whitespace, don't save it.
        content = content.strip()
        if content:
            clean_content = bleach.clean(content)
            # Save it in the database
            add_post(clean_content)
    # 302 redirect back to the main page
    headers = [('Location', '/'),
               ('Content-type', 'text/plain')]
    resp('302 REDIRECT', headers) 
    return [b'Redirecting']

## Dispatch table - maps URL prefixes to request handlers
DISPATCH = {'': View,
            'post': Post,
	    }

## Dispatcher forwards requests according to the DISPATCH table.
def Dispatcher(env, resp):
    '''Send requests to handlers based on the first path component.'''
    page = util.shift_path_info(env)
    if page in DISPATCH:
        return DISPATCH[page](env, resp)
    else:
        status = '404 Not Found'
        headers = [('Content-type', 'text/plain')]
        resp(status, headers)    
        return [('Not Found: ' + page).encode()]


# Run this bad server only on localhost!
# PORT wins; locally the default is 3100, the first port of soulcraft's dev block.
port = int(os.environ.get('PORT', 3100))
httpd = make_server('', port, Dispatcher)
print ("Serving HTTP on port {}...".format(port))
httpd.serve_forever()
