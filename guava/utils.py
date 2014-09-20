#!/usr/bin/env python
# -*- coding: utf-8 -*-

import string
import random

import simplejson as json
import datetime
from bson import ObjectId

import pytz

def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))



class BaseJSONEncoder(json.JSONEncoder):
    """ Proprietary JSONEconder subclass used by the json render function.
    This is needed to address the encoding of special values.
    """
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            # convert any datetime to RFC 1123 format
            obj.replace(tzinfo=pytz.utc)
            return obj.isoformat()
        elif isinstance(obj, (datetime.time, datetime.date)):
            # should not happen since the only supported date-like format
            # supported at dmain schema level is 'datetime' .
            try:
                obj.replace(tzinfo=pytz.utc)
            except:
                pass
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


class MongoJSONEncoder(BaseJSONEncoder):
    """ Proprietary JSONEconder subclass used by the json render function.
    This is needed to address the encoding of special values.

    .. versionadded:: 0.2
    """
    def default(self, obj):
        if isinstance(obj, ObjectId):
            # BSON/Mongo ObjectId is rendered as a string
            return str(obj)
        else:
            # delegate rendering to base class method
            return super(MongoJSONEncoder, self).default(obj)