# -*- coding: UTF-8 -*- #

import unittest

import os
from Locales.Locales import Locales
from flask import Flask, session, g, Blueprint
from tests.WithContext import WithContext
from tests.config import CONFIG

# blueprints using a common templates folder
blueprint = Blueprint(u'blueprint', __name__)


class ContextTestCase(WithContext, unittest.TestCase):
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

    def test_templates_can_access_other_locales(self):
        """
        Other locales can be accessed within a template using either:
        dot notation, as in zh_Hans.key, or
        dict notation, as in zh_Hans['key']
        """

        context = {
            u'en': {},
            u'zh_Hans': {
                u'key': u'value'
            }
        }

        g.locales.set(u'en')

        self.assertEqual(
            g.locales.render_template(u'other_locale.html', **context),
            u'\n'.join([u'value', u'value'])
        )

    def test_render_template_by_name(self):
        """
        Should be able to render a template by specifying only the template name and the context name, and the correct files will be selected
        :return:
        """
        g.locales.set(u'en')
        result = g.locales.render_template(u'template.html', u'context.yaml').split()

        self.assertEqual(result[0], u'en/template.html')
        self.assertEqual(result[1], u'en/context.yaml')

        g.locales.set(u'zh_Hans')
        result = g.locales.render_template(u'template.html', u'context.yaml').split()

        self.assertEqual(result[0], u'zh_Hans/template.html')
        self.assertEqual(result[1], u'zh_Hans/context.yaml')

    def test_render_with_extra_context(self):
        """
        Should be able to render a template by specifying the template name and the context name, and still pass keyword variables to the context
        :return:
        """

        ctx = {u'other': u'extra'}

        g.locales.set(u'en')
        result = g.locales.render_template(u'template.html', u'context.yaml', **ctx).split()

        self.assertEqual(result[0], u'en/template.html')
        self.assertEqual(result[1], u'en/context.yaml')
        self.assertEqual(result[2], u'extra')

        g.locales.set(u'zh_Hans')
        result = g.locales.render_template(u'template.html', u'context.yaml', **ctx).split()

        self.assertEqual(result[0], u'zh_Hans/template.html')
        self.assertEqual(result[1], u'zh_Hans/context.yaml')
        self.assertEqual(result[2], u'extra')

    def test_render_with_no_context_name_but_extra_context(self):
        """
        Should be able to render a template by specifying the template name but no context name, and still pass keyword variables to the context
        :return:
        """

        ctx = {u'other': u'extra'}

        g.locales.set(u'en')
        result = g.locales.render_template(u'template.html', **ctx).split()

        self.assertEqual(result[0], u'en/template.html')
        self.assertEqual(result[1], u'extra')

        g.locales.set(u'zh_Hans')
        result = g.locales.render_template(u'template.html', **ctx).split()

        self.assertEqual(result[0], u'zh_Hans/template.html')
        self.assertEqual(result[1], u'extra')
