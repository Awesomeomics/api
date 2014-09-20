#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bcrypt

from flask import Blueprint, request, abort
from flask import current_app as app
from authentication import encrypt_password, verify_password
from authentication import from_refresh_token, generate_token

auth = Blueprint('auth', __name__)

@auth.route('/auth/email', methods=['POST'])
def authenticate():

	data = request.json
	if not data:
		abort(400)

	email = data.get('email')
	password = data.get('password')

	if not email or not password:
		abort(400)

	client = app.db['clients'].find_one({'email': email})
	if not client or not verify_password(password, client.get('password')):
		abort(403, 'invalid credentials')

	token_resp = generate_token(str(client['_id']))
	return jsonify(token_resp)


@auth.route('/auth/refresh', methods=['GET'])
def refresh_handler():
	if not request.args.get('refresh_token'):
		abort(400, 'missing refresh token')

	token = from_refresh_token(request.args['refresh_token'])
	if token:
		return jsonify(token)
	abort(403)
	


