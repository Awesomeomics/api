#!/usr/bin/env python
# -*- coding: utf-8 -*-

import settings
import json

from pymongo import MongoClient

client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
mongo = client[settings.MONGO_DB]

def load_hpo():

	if not mongo['HPO'].find_one():
		hpo_file = open('/'.join([settings.RESOURCES_PATH, 'hpo2gene.json']))
	  	hpo = json.loads(hpo_file.read())

	  	payload = []
	  	for key, val in hpo.iteritems():
	  		payload.append({'hpo_term': key, 'genes': val})
	  	
	  	mongo['HPO'].insert(payload)


