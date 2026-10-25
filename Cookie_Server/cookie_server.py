# An HTTP server that remembers a user name in a HTTP cookie

from http.cookies import SimpleCookie, CookieError
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from http import cookies
from urllib.parse import parse_qs
from html import escape as html_escape

form = '''<!DOCTYPE html>
<title>I Remember You</title>
<p>
{}
<p>
<form method="POST">
<label>What's your name again?
<input type="text" name="yourname">
</label>
<br>
<button type="submit">Tell me!</button>
</form>
'''


class NameHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        '''Post Function'''
        # Post Data Length
        length = int(self.headers.get('Content-length', 0))

        # Read and Parse the post data
        data = self.rfile.read(length).decode()
        yourname = parse_qs(data)["yourname"][0]

        # Create cookie
        c = cookies.SimpleCookie()
        c['yourname'] = yourname
        c['yourname']['domain'] = 'localhost'
        c['yourname']['max-age'] = 60


        # Send a 303 back to the root page, with a cookie!
        self.send_response(303)  # redirect via GET
        self.send_header('Location', '/')
        self.send_header('Set-Cookie', c['yourname'].OutputString())
        self.end_headers()

    def do_GET(self):
        '''Get Function'''
        # Default message if we don't know a name
        message = "I don't know you yet!"

        # Look for a cookie in the request
        if 'cookie' in self.headers:
            try:
                c = cookies.SimpleCookie(self.headers['cookie'])
                name = c['yourname'].value

                # Craft a message, escaping any HTML special chars in name
                message = "Hey there, " + html_escape(name)
            except (KeyError, cookies.CookieError) as e:
                message = "I'm not sure who you are!"
                print(e)

        # First, send a 200 OK response
        self.send_response(200)

        # Then send headers.
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

        # Send the form with the message in it
        mesg = form.format(message)
        self.wfile.write(mesg.encode())


if __name__ == '__main__':
    # PORT wins; locally the default is 3100, the first port of soulcraft's dev block.
    server_address = ('', int(os.environ.get('PORT', 3100)))
    httpd = HTTPServer(server_address, NameHandler)
    httpd.serve_forever()
