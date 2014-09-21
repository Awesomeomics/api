#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify
from flask import current_app as app
from authentication import requires_auth
from xdomains import crossdomain

hpo = Blueprint('hpo', __name__)

@hpo.route('/hpo', methods=['GET'])
@crossdomain()
def get_hpo():

	q = request.args.get('q')
	if q:
		query = {'hpo_term': {'$regex': q, '$options': 'i'}}
	else:
		query = {}

	results = list(app.db['HPO'].find(query).limit(10))
	return jsonify({'data': results})