#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from flask import Blueprint, jsonify, request, abort, redirect
from flask import current_app as app
from werkzeug import secure_filename
from tasks import annotate_vcf, persist_csv
from datetime import datetime
import pytz

from authentication import requires_auth

from bson import ObjectId

from xdomains import crossdomain

patient = Blueprint('patient', __name__)

@patient.route('/patient', methods=['POST', 'OPTIONS'])
@crossdomain()
@requires_auth
def annotate(client):

	data = request.form
	if not data:
		abort(400)
	data = dict(data)
	data.pop('file', None)

	if not data.get('sampleId'):
		abort(400, "missing field 'sampleId'")


	data['_created']=data['_updated'] = datetime.utcnow().replace(microsecond=0).replace(tzinfo=pytz.utc)
	
	if not app.db['patients'].find_one({'sampleId': data['sampleId']}):
		pid = str(app.db['patients'].insert(data))

	app.db['projects'].insert({'clientId': ObjectId(client), 'patientId': ObjectId(pid)})

	def allowed_file(filename):
		return '.' in filename and \
			filename.rsplit('.', 1)[1] in ['vcf']

	file = request.files['file']
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		annotate_vcf.apply_async((filename,), link=persist_csv.s(pid))
		return redirect('http://localhost:5555')
		#return jsonify({'status': 'ok'})

	resp = jsonify({'status': 'err'})
	resp.status_code = 400
	return resp


@patient.route('/patient/<regex("[a-f0-9]{24}"):pid>', methods=['GET', 'POST', 'OPTIONS'])
@crossdomain()
@requires_auth
def query(client, pid):

	if not app.db['projects'].find_one({'clientId': ObjectId(client), 'patientId': ObjectId(pid)}):
		abort(403)

	if request.method == 'GET':
		return jsonify(app.db['patients'].find_one({'_id': ObjectId(pid)}))

	limit = request.args.get('limit', 20)
	page = int(request.args.get('page', 1))
	skip = limit * (page - 1)

	query = request.json

	response = app.db['PATIENT_%s' % pid].find(query).skip(skip).limit(limit)
	return jsonify({'results': list(response)})