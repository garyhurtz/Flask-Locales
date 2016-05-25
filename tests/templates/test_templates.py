# -*- coding: UTF-8 -*- #

import unittest
import os
from flask import Flask, session, g, Blueprint
from Locales.Locales import Locales
from tests.WithContext import WithContext
from tests.config import CONFIG

# blueprints using a common templates folder
blueprint = Blueprint(u'blueprint', __name__)


class TemplatesTestCase(WithContext, unittest.TestCase):
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

    def beforeEach(self):
        # reset session before each test
        session[u'locale'] = None

    def afterEach(self):
        pass

    def test_setup(self):
        """
        tests should be set up correctly
        """
        # session starts with no locale
        self.assertIsNone(session.get(u'locale'))

        # g has locale attached
        self.assertIsInstance(g.locales, Locales)

        # Confirm that the template searchpath is as expected
        self.assertEqual(
            self.app.jinja_loader.searchpath,
            [os.path.dirname(__file__) + u'/templates']
        )

        # Confirm that Flask detects all of the templates
        self.assertItemsEqual(self.app.jinja_loader.list_templates(), [
            u'template.html',
            u'en/template.html',
            u'zh_Hans/template.html',
            u'blueprint/template.html',
            u'blueprint/en/template.html',
            u'blueprint/zh_Hans/template.html'
        ])

    def test_locales_will_use_the_localed_template_if_available(self):

        g.locales.set(u'en')

        self.assertEqual(
            g.locales.render_template(u'template.html'),
            u'en/template.html'
        )

        g.locales.set(u'zh_Hans')

        self.assertEqual(
            g.locales.render_template(u'template.html'),
            u'zh_Hans/template.html'
        )

    def test_locales_will_use_the_localed_template_if_available_with_blueprints_too(self):

        g.locales.set(u'en')

        self.assertEqual(
            g.locales.render_template(u'blueprint/template.html'),
            u'blueprint/en/template.html'
        )

        g.locales.set(u'zh_Hans')

        self.assertEqual(
            g.locales.render_template(u'blueprint/template.html'),
            u'blueprint/zh_Hans/template.html'
        )
