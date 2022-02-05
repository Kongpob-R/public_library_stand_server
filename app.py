from flask import Flask  

app = Flask(__name__) # name for the Flask app (refer to output)
# running the server
app.run(debug = True) # to allow for debugging and auto-reload