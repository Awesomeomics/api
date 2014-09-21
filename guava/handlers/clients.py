#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bcrypt

from flask import Blueprint, request, abort, jsonify
from flask import current_app as app
from authentication import encrypt_password, verify_password
from authentication import from_refresh_token, generate_token, requires_auth

from datetime import datetime
import pytz

from bson import ObjectId

from xdomains import crossdomain

clients = Blueprint('client', __name__)

@clients.route('/clients', methods=['POST', 'OPTIONS'])
@crossdomain()
def add_client():

	data = request.json
	if not data:
		abort(400)

	firstname = data.get('firstname')
	lastname = data.get('lastname')
	email = data.get('email')
	password = data.get('password')

	# todo validate email/password

	if not email or not password or not firstname or not lastname:
		abort(400)

	client = app.db['clients'].find_one({'email': email})
	if client:
		abort(400, 'account already exists')

	payload = {'firstname': firstname,
			   'lastname': lastname,
			   'email': email,
			   'password': encrypt_password(password)}

	payload['_created'] = payload['_updated'] = datetime.utcnow().replace(microsecond=0).replace(tzinfo=pytz.utc)

	clientId = app.db['clients'].insert(payload)

	token_resp = generate_token(str(clientId))
	return jsonify(token_resp)


@clients.route('/clients/<regex("[a-f0-9]{24}"):cid>', methods=['GET', 'OPTIONS'])
@crossdomain()
@requires_auth
def get_client(client, cid):

	if not client == cid:
		abort(403)
	
	client = app.db['clients'].find_one({'_id': ObjectId(cid)}, {'password': 0})
	if client:
		return jsonify(client)
	abort(404)


@clients.route('/patients', methods=['GET', 'OPTIONS'])
@crossdomain()
@requires_auth
def get_patients(client):
	
	projects = app.db['projects'].find({'clientId': ObjectId(client)}, {'patientId': 1})
	patients = [project['patientId'] for project in projects]
	patients = list(app.db['patients'].find({'_id': {'$in': patients}}))
	
	for patient in patients:
		if app.db['PATIENT_%s' % str(patient['_id'])].find_one():
			patient['status'] = 'ready'
		else:
			patient['status'] = 'pending'
	return jsonify({'data': patients})



