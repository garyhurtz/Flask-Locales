# -*- coding: UTF-8 -*- #

"""
Helper script to synchronize yaml and json for speed comparison tests
"""

import codecs
from flask import json
import yaml

with codecs.open(u'time_test.yaml', u'r', u'utf-8') as infile:
    context = yaml.load(infile)

with codecs.open(u'time_test.json', u'w', u'utf-8') as outfile:
    json.dump(context, outfile)
