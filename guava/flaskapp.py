#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import sys
sys.path.append('guava/')

import redis
import settings

from pymongo import MongoClient
from flask import Flask, jsonify

from handlers.patient import patient
from handlers.auth import auth
from handlers.clients import clients
from handlers.hpo import hpo

from werkzeug.exceptions import default_exceptions, HTTPException
from werkzeug.routing import BaseConverter
from utils import MongoJSONEncoder

from prepare import load_hpo

def JSONApp(import_name, **kwargs):



    def make_json_error(ex):
        response = jsonify(message=str(ex))
        response.status_code = (ex.code
                                if isinstance(ex, HTTPException)
                                else 500)
        h = response.headers

        h['Access-Control-Allow-Origin'] = '*'
        h['Access-Control-Max-Age'] = str(21600)
        h['Access-Control-Allow-Headers'] = 'CONTENT-TYPE'

        return response

    app = Flask(import_name, **kwargs)

    for code in default_exceptions.iterkeys():
        app.error_handler_spec[None][code] = make_json_error

    return app


app = JSONApp(__name__)
app.config.from_pyfile('settings.py')

app.json_encoder = MongoJSONEncoder

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

app.url_map.converters['regex'] = RegexConverter

client = MongoClient(app.config['MONGO_HOST'], app.config['MONGO_PORT'])
app.db = client[app.config['MONGO_DB']]

app.redis = redis.StrictRedis(host=settings.REDIS_HOST,
                          port=settings.REDIS_PORT,
                          db=settings.REDIS_DB,
                          password=settings.REDIS_PASSWORD)


app.register_blueprint(patient)
app.register_blueprint(auth)
app.register_blueprint(clients)
app.register_blueprint(hpo)

if __name__ == '__main__':

    load_hpo()
    app.run()