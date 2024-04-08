from flask import Flask, Request, jsonify, request
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


@app.route('/')
def inicio():
    return 'No sale'

#INICIAR
if __name__ == ('__main__'):
    app.run(port=8880, debug=True)