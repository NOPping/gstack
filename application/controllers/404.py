from application import app
from flask import jsonify, Response

@app.errorhandler(404)
def not_found(error=None):
    message = {
            'status': 404,
            'message': 'Not Found'
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp