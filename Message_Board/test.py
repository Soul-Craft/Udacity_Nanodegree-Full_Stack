'''
Test script for the Messageboard

The server should be listening on port $PORT (default 3100), 
answer a GET request with an HTML document, 
and answer a POST request with a redirect to the main page.
'''

# Import Modules
import os, requests, random, socket, sys

PORT = int(os.environ.get('PORT', 3100))
BASE = 'http://localhost:{}/'.format(PORT)

def test_connect():
    '''Try connecting to the server.'''
    print("Testing connecting to the server.")
    try:
        with socket.socket() as s:
           s.connect(("localhost", PORT))
        print("Connection attempt succeeded.")
        return None
    except socket.error:
        return "Server didn't answer on localhost port {}.  Is it running?".format(PORT)

def test_POST_303():
    '''The server should accept a POST and return a 303 to /.'''
    print("Testing POST request, looking for redirect.")
    mesg = random.choice(["Hi there!", "Hello!", "Greetings!"])
    uri = BASE
    try:
        r = requests.post(uri, data = {'message': mesg}, allow_redirects=False)
    except requests.RequestException as e:
        return ("Couldn't communicate with the server. ({})\n"
                "If it's running, take a look at its output.").format(e)
    if r.status_code == 501:
        return ("The server returned status code 501 Not Implemented.\n"
                "This means it doesn't know how to handle a POST request.\n"
                "(Is the correct server code running?)")
    elif r.status_code != 303:
        return ("The server returned status code {} instead of a 303 redirect."
                ).format(r.status_code)
    elif r.headers['location'] != '/':
        return ("The server sent a 303 redirect to the wrong location."
                "I expected '/' but it sent '{}'.").format(
                    r.headers['location'])
    else:
        print("POST request succeeded.")
        return None

def test_GET():
    '''The server should accept a GET and return the form.'''
    print("Testing GET request.")
    uri = BASE
    try:
        r = requests.get(uri)
    except requests.RequestException as e:
        return ("Couldn't communicate with the server. ({})\n"
                "If it's running, take a look at its output.").format(e)
    if r.status_code == 501:
        return ("The server returned status code 501 Not Implemented.\n"
                "This means it doesn't know how to handle a GET request.\n"
                "(Is the correct server code running?)")
    elif r.status_code != 200:
        return ("The server returned status code {} instead of a 200 OK."
                ).format(r.status_code)
    elif not r.headers['content-type'].startswith('text/html'):
        return ("The server didn't return Content-type: text/html.")
    elif '<title>Message Board</title>' not in r.text:
        return ("The server didn't return the form text I expected.")
    else:
        print("GET request succeeded!")
        return None

def test_memory():
    '''The server should remember posts.'''
    print("Testing whether messageboard saves messages.")
    uri = BASE
    mesg = random.choice(["Remember me!", "Don't forget.", "You know me."])
    r = requests.post(uri, data = {'message': mesg})
    if r.status_code != 200:
        return ("Got status code {} instead of 200 on Post-Redirect-Get."
                ).format(r.status_code)
    elif mesg not in r.text:
        return ("I posted a message but it didn't show up.\n"
                "Expected '{}' to appear, but got this output instead:\n"
                "{}").format(mesg, r.text)
    else:
        print("Post-Redirect-Get succeeded and I saw my message!")

if __name__ == '__main__':
    tests = [test_connect, test_POST_303, test_GET, test_memory]
    for test in tests:
        problem = test()
        if problem is not None:
            print(problem)
            break
    if problem:
        sys.exit(1)
    print("All tests succeeded!")
