# -*- coding: UTF-8 -*- #

import unittest
import pprint
from datetime import datetime

from Locales.Locales import Locales
from Locales.Loaders import yaml_loader, json_loader, json_caching_yaml_loader
from flask import Flask, g, Blueprint
from tests.WithContext import WithContext
from tests.config import CONFIG

# blueprints using a common templates folder
blueprint = Blueprint(u'blueprint', __name__)


class ContextLoadTimingTestCase(WithContext, unittest.TestCase):
    """
    Test Strategies

     - each template returns a string containing its path. This way I can easily confirm which template rendered by simply checking the returned string.

    """

    def create_app(self):
        app = Flask(__name__, template_folder=u'templates')
        app.config.from_object(CONFIG)

        app.register_blueprint(blueprint)

        Locales(app)

        return app

    def test_load_localed_context(self):
        """
        If the specified file is located within the current locale's context folder, load it
        :return:
        """

        results = dict()
        filename = u'time_test'

        for i in (1, 10, 100):

            cum_yaml = 0.
            cum_jcyl = 0.
            cum_json = 0.

            for j in range(i):

                start = datetime.utcnow()
                Locales.context_loader = yaml_loader
                context = g.locales.load(u'{0}.yaml'.format(filename))
                end = datetime.utcnow()
                cum_yaml += (end - start).microseconds

                start = datetime.utcnow()
                Locales.context_loader = json_loader
                context = g.locales.load(u'{0}.json'.format(filename))
                end = datetime.utcnow()
                cum_json += (end - start).microseconds

                start = datetime.utcnow()
                Locales.context_loader = json_caching_yaml_loader
                context = g.locales.load(u'{0}.yaml'.format(filename))
                end = datetime.utcnow()
                cum_jcyl += (end - start).microseconds

            results[unicode(i)] = {
                u'json': cum_json,
                u'yaml': cum_yaml,
                u'jcyl': cum_jcyl
            }

        print u'Loader timing comparison'
        pprint.pprint(results)
