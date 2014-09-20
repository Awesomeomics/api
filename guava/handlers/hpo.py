#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint
from authentication import requires_auth

hpo = Blueprint('hpo', __name__)

@hpo.route('/hpo', methods=['GET'])
@requires_auth
def get_hpo(client):

	return 'hpo'