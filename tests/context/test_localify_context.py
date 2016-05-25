# -*- coding: UTF-8 -*- #
import unittest

from Locales.Locales import Locales
from flask import Flask, session, g, Blueprint
from tests.WithContext import WithContext
from tests.config import CONFIG

__author__ = 'gary'

# blueprints using a common templates folder
blueprint = Blueprint(u'blueprint', __name__)


class LocalifyContextTestCase(WithContext, unittest.TestCase):

    def create_app(self):
        app = Flask(__name__, template_folder=u'templates')
        app.config.from_object(CONFIG)

        app.register_blueprint(blueprint)

        Locales(app)

        return app

    def beforeEach(self):
        # reset session before each test
        session[u'locale'] = None

    def test_localify_context_default_makes_no_change(self):
        context = {u'greeting': u'Hello'}

        self.assertEqual(g.locales._localify_context(**context), context)

    def test_localify_context_default_makes_no_change_with_kws_too(self):
        context = {u'greeting': u'Hello'}

        self.assertEqual(g.locales._localify_context(greeting=u'Hello'), context)

    def test_localify_context_promotes_current_locale(self):
        context = {
            u'en': {u'greeting': u'Hello'},
            u'zh_Hans': {u'greeting': u'你好'}
        }

        g.locales.set(u'en')
        expected = {
            u'greeting': u'Hello',
            u'en': {u'greeting': u'Hello'},
            u'zh_Hans': {u'greeting': u'你好'}
        }
        self.assertEqual(g.locales._localify_context(**context), expected)

        g.locales.set(u'zh_Hans')
        expected = {
            u'greeting': u'你好',
            u'en': {u'greeting': u'Hello'},
            u'zh_Hans': {u'greeting': u'你好'}
        }
        self.assertEqual(g.locales._localify_context(**context), expected)
