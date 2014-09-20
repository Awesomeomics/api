#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

DEBUG = True

CELERY_BROKER_URL='amqp://'
CELERY_RESULT_BACKEND='amqp://'

CELERY_TASK_SERIALIZER='json'
CELERY_RESULT_SERIALIZER='json'
CELERY_ACCEPT_CONTENT=['json']


MONGO_PORT = 27017
MONGO_HOST = 'localhost'
MONGO_DB = 'guavaTest'


ANNOVAR_PATH = r"%s/annovar" % '/'.join(os.path.dirname(os.path.abspath(__file__)).split('/')[:-1]) 
UPLOAD_FOLDER =ANNOVAR_PATH


ANNOTATION_TYPES = {
	'Chr': 'text',
	'Start': 'int',
	'End': 'int',
	'Ref': 'text',
	'Alt': 'text',
	'Func.refGene': 'text',
	'Gene.refGene': 'text',
	'GeneDetail.refGene': 'text',
	'ExonicFunc.refGene': 'text',
	'AAChange.refGene': 'text',
	'esp6500si_all': 'float',
	'LJB26_Polyphen2_HDIV_pred': 'text',
	'LJB26_Polyphen2_HVAR_score': 'float',
    'clinvar_20140902': 'text',
    'Otherinfo': 'text'
}