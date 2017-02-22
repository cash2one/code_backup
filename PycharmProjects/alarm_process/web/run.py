#!flask/bin/python

from web.app import app
app.run(port=9100, host='0.0.0.0', debug=True)
