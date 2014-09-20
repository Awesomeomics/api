#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from flask import Blueprint, jsonify, request, abort
from flask import current_app as app
from werkzeug import secure_filename
from tasks import annotate_vcf, persist_csv
from datetime import datetime
import pytz

from authentication import requires_auth

from bson import ObjectId

patient = Blueprint('patient', __name__)

@patient.route('/patient', methods=['POST'])
@requires_auth
def annotate(client):

	data = request.form
	if not data:
		abort(400)
	data = dict(data)

	if not data.get('sampleId'):
		abort(400, "missing field 'sampleId'")

	data['_created']=data['_updated'] = datetime.utcnow().replace(microsecond=0).replace(tzinfo=pytz.utc)
	pid = str(app.db['patients'].insert(data))

	app.db['projects'].insert({'clientId': ObjectId(client), 'patientId': ObjectId(patient)})

	def allowed_file(filename):
		return '.' in filename and \
			filename.rsplit('.', 1)[1] in ['vcf']

	file = request.files['file']
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		annotate_vcf.apply_async((filename,), link=persist_csv.s(pid))
		return jsonify({'status': 'ok'})

	resp = jsonify({'status': 'err'})
	resp.status_code = 400
	return resp


@patient.route('/patient/<regex("[a-f0-9]{24}"):pid>', methods=['GET', 'POST'])
@requires_auth
def query(client, pid):

	if not app.db['projects'].find_one({'clientId': ObjectId(client), 'patientId': ObjectId(pid)}):
		abort(403)

	limit = request.args.get('limit', 50)
	page = request.args.get('page': 1)
	skip = limit * (page - 1)

	query = {}
	response = app.db['PATIENT_%s' % pid].find(query).skip(skip).limit(limit)
	return jsonify(response)