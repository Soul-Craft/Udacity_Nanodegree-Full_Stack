# A demonstration that your browser opens many requests to a server.

import http.server, os, threading, time, random

'''
HTML main page.
This page has 16 iframes,
each of which causes the browser to send an additional request to this server.
Each iframe will display the number of currently active requests.
'''

html = '''
        <!DOCTYPE html>
        <title>Things!</title>
        <style>iframe { width: 23%; border: 0 }</style>
        <iframe src="/frame0"></iframe> <iframe src="/frame1"></iframe>
        <iframe src="/frame2"></iframe> <iframe src="/frame3"></iframe>
        <iframe src="/frame4"></iframe> <iframe src="/frame5"></iframe>
        <iframe src="/frame6"></iframe> <iframe src="/frame7"></iframe>
        <iframe src="/frame8"></iframe> <iframe src="/frame9"></iframe>
        <iframe src="/framea"></iframe> <iframe src="/frameb"></iframe>
        <iframe src="/framec"></iframe> <iframe src="/framed"></iframe>
        <iframe src="/framee"></iframe> <iframe src="/framef"></iframe>
        '''

'''
Track the number of requests that are in progress.
This variable will get +1 every time a handler starts processing a request,
and -1 every time it finishes.
'''
inflight = 0
'''
To protect the inflight variable 
from being changed from multiple request handlers at once,
we need to use a lock.
'''
lock = threading.Lock()


class Parallelometer(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global inflight, lock
        with lock:
            # Starting to handle a request.
            inflight += 1
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        if self.path.startswith('/frame'):

            # This request is for iframe contents.
            time.sleep(random.random())  # Slow down by 0-1 seconds.
            self.wfile.write('{} requests in flight'.format(inflight).encode())
        else:

            # This request is for the main page.
            self.wfile.write(html.encode())
            self.wfile.flush()
        with lock:

            # Done handling a request.
            inflight -= 1


if __name__ == '__main__':
    # PORT wins; locally the default is 3100, the first port of soulcraft's dev block.
    address = ('', int(os.environ.get('PORT', 3100)))
    # ThreadingHTTPServer (Python 3.7+) handles each request in its own thread.
    httpd = http.server.ThreadingHTTPServer(address, Parallelometer)
    httpd.serve_forever()
