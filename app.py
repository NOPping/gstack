from flask import Flask, jsonify, Response
app = Flask(__name__)

@app.route('/')
def api_root():
    message = {
            'status': 200,
            'message': 'Hello World'
    }
    resp = jsonify(message)
    resp.status_code = 200

    return resp

@app.errorhandler(404)
def not_found(error=None):
    message = {
            'status': 404,
            'message': 'Not Found'
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp

if __name__ == '__main__':
    app.run(debug=True)