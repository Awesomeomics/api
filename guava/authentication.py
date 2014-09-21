#!/usr/bin/env python
# -*- coding: utf-8 -*-

import bcrypt
import json
import pytz
import string
import random
import base64

from flask import current_app as app
from flask import request, abort

from datetime import datetime, timedelta
from functools import wraps

def encrypt_password(password):
	return bcrypt.hashpw(password, bcrypt.gensalt())

def verify_password(password, hashed):
	return bcrypt.hashpw(password, hashed) == hashed


def gen_tok():
	return base64.urlsafe_b64encode(generate_random_string(random.randint(50, 75), string.hexdigits)).replace('=', '')

 
def generate_token(clientId):

	data = {'clientId': clientId}
	access_token = gen_tok()
	refresh_token = gen_tok()
	expires_in = 60 * 60 * 4 # 4hrs

	persist_token_information(access_token, expires_in, refresh_token, data)

	return token_response(access_token, refresh_token, expires_in, clientId)


def persist_token_information(access_token, expires_in, refresh_token, data):

	access_key = 'access_token:%s' % access_token
	app.redis.setex(access_key, expires_in, json.dumps(data))

	refresh_key = 'refresh_token:%s' % refresh_token
	app.redis.set(refresh_key, json.dumps(data))

	#TODO Setup HSet


def from_refresh_token(refresh_token):
	key = 'refresh_token:%s' % refresh_token
	data = app.redis.get(key)
	discard_refresh_token(refresh_token)

	if data is not None:
		data = json.loads(data)
	else:
		return None

	refresh_token = gen_tok()
	access_token = gen_tok()
	expires_in = 60*60*4

	persist_token_information(access_token, expires_in, refresh_token, data)

	return token_response(access_token, refresh_token, expires_in, data['clientId'])

def discard_refresh_token(refresh_token):
	key = 'refresh_token:%s' % refresh_token
	app.redis.delete(key)


def token_response(access_token, refresh_token, expires_in, clientId):
	return {'access_token': access_token, 'refresh_token': refresh_token, 
			'expires': (datetime.utcnow() + timedelta(seconds=expires_in)).replace(tzinfo=pytz.utc).replace(microsecond=0).isoformat(),
			'created': datetime.utcnow().replace(tzinfo=pytz.utc).replace(microsecond=0).isoformat(),
			'_id': clientId}


def token_lookup(access_token):
	key = 'access_token:%s' % access_token
	data = app.redis.get(key)
	if date is not None:
		return json.loads(data)
	return None


def requires_auth(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		if not request.args.get('access_token'):
			abort(403, "missing" 'access_token')

		data = token_lookup(request.args['access_token'])
		if not data:
			abort(403)

		return f(str(data['clientId']), *args, **kwargs)
	return wrapper