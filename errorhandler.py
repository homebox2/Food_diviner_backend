# -*- coding: utf8 -*-
import json
from flask import Flask,Response

application = Flask(__name__)

@application.errorhandler(405)
def handle_405(error):
    js = json.dumps({'message': 'Method not allowed'})
    resp = Response(js, status=405, mimetype='application/json')
    return resp


@application.errorhandler(404)
def handle_404(error):
    js = json.dumps({'message': 'Method not defined'})
    resp = Response(js, status=404, mimetype='application/json')
    return resp


@application.errorhandler(501)
def handle_501(error):
    resp = Response(json.dumps({'message': 'Method not implemented'}), status=501, mimetype='application/json')
    return resp


@application.errorhandler(500)
def handle_500(error):
    resp = Response(json.dumps({'message': 'Unknown error'}), status=500, mimetype='application/json')
    return resp