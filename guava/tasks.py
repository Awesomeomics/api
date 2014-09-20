#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import sys
sys.path.append('guava/')

import os
import settings
import subprocess
import csv
import re

from celery import Celery
from pymongo import MongoClient

from utils import id_generator

app = Celery('guava', broker=settings.CELERY_BROKER_URL, include=['tasks'])
app.config_from_object(settings)

client = MongoClient(settings.MONGO_HOST, settings.MONGO_PORT)
mongo = client[settings.MONGO_DB]


@app.task
def annotate_vcf(filename):

	prefix = id_generator()

	cmd = "./table_annovar.pl %s humandb/ -buildver hg19 -out %s" \
	      " -remove -protocol refGene,esp6500si_all,ljb26_pp2hvar,clinvar_20140902" \
	      " -operation g,f,f,f -nastring . -vcfinput -csvout" % (filename, prefix)

	subprocess.call(cmd, cwd=settings.ANNOVAR_PATH, shell=True)

	return '%s.hg19_multianno.csv' % (prefix)

@app.task
def persist_csv(filename, patient):

	absolute_file = r"%s/%s" % (settings.ANNOVAR_PATH, filename)

	collection = mongo['PATIENT_%s'%patient]
	collection.remove()

	with open(absolute_file, 'rb') as csvfile:
		dialect = csv.Sniffer().sniff(csvfile.read(1024))
		csvfile.seek(0)
		annotated = csv.reader(csvfile, dialect)
		headers = annotated.next()

		payload = []
 		for row in annotated:
 			r = {}
 			for i in range(len(headers)):
				try:
					val = float(row[i])
				except:
					val = row[i] if row[i] != '.' else None
 				r[headers[i].replace('.', '_')] = val
 			payload.append(r)
 		collection.insert(payload)
 	
 	def purge(dir, pattern):
 		for f in os.listdir(dir):
 			if re.search(pattern, f):
 				os.remove(os.path.join(dir, f))

 	prefix = filename.split('.', 1)[0]
 	purge(settings.ANNOVAR_PATH, prefix)

if __name__=='__main__':
	app.start()