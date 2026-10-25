"""
THIS IS A WEBSERVER 
FOR DEMONSTRATING THE TYPES OF RESPONSES
FROM AN API ENDPOINT
"""

# Import Flask
import os
from flask import Flask

app = Flask(__name__)

# GET REQUEST
@app.route('/readHello/', methods = ['GET'])
def getRequestHello():
	
	return "Hi, I got your GET Request!"

# POST REQUEST
@app.route('/createHello/', methods = ['POST'])
def postRequestHello():
	
	return "I see you sent a POST message :-)"

# UPDATE REQUEST
@app.route('/updateHello/', methods = ['PUT'])
def updateRequestHello():
	
	return "Sending Hello on an PUT request!"

# DELETE REQUEST
@app.route('/deleteHello/', methods = ['DELETE'])
def deleteRequestHello():
	
	return "Deleting your hard drive.....haha just kidding! I received a DELETE request!"

if __name__ == '__main__':
    app.debug = True
    # PORT wins; locally the default is 3100, the first port of soulcraft's dev block (5000 is AirPlay's on a Mac).
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3100)))	