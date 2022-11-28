from flask import Flask, request
from flask_cors import CORS, cross_origin
import flapc

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/compute", methods=['POST'])
def compute():
    return flapc.compute(request.json)

if __name__ == "__main__":
    app.run()
