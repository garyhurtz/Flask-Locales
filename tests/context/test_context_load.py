# -*- coding: UTF-8 -*- #

import unittest

import codecs
import os
from Locales.Locales import Locales
from Locales.Loaders import json_caching_yaml_loader
from flask import Flask, session, g, Blueprint, json, current_app
from tests.WithContext import WithContext
from tests.config import CONFIG

# blueprints using a common templates folder
blueprint = Blueprint(u'blueprint', __name__)


class ContextLoadTests(object):

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

    def test_load_localed_context(self):
        """
        If the specified file is located within the current locale's context folder, load it
        :return:
        """
        g.locales.current = u'en'
        context = g.locales.load(u'localed_context.yaml')

        self.assertEqual(
            context.get(u'path'),
            u'en/localed_context.yaml'
        )

        g.locales.current = u'zh_Hans'
        context = g.locales.load(u'localed_context.yaml')

        self.assertEqual(
            context.get(u'path'),
            u'zh_Hans/localed_context.yaml'
        )

    def test_load_localed_context_with_blueprint(self):
        """
        If the specified file is located within the current locale's context folder, load it
        :return:
        """
        g.locales.current = u'en'
        context = g.locales.load(u'blueprint/localed_context.yaml')

        self.assertEqual(
            context.get(u'path'),
            u'blueprint/en/localed_context.yaml'
        )

        g.locales.current = u'zh_Hans'
        context = g.locales.load(u'blueprint/localed_context.yaml')

        self.assertEqual(
            context.get(u'path'),
            u'blueprint/zh_Hans/localed_context.yaml'
        )

    def test_load_common_context(self):
        """
        if the specified file is not in the current locale's context folder, check for it at the root of the context folder
        """
        context = g.locales.load(u'common_context.yaml')

        self.assertEqual(
            context.get(u'path'),
            u'context/common_context.yaml'
        )

    def test_load_common_context_with_blueprint(self):
        """
        if the specified file is not in the current locale's context folder, check for it at the root of the context folder
        """

        context = g.locales.load(u'blueprint/common_context.yaml')

        self.assertEqual(
            context.get(u'path'),
            u'blueprint/common_context.yaml'
        )

    def test_load_alt_common_context(self):
        """
        If the specified file is not in either the current locale's context folder or at the root of the context folder, check if this is an alternative common context
        :return:
        """

        context = g.locales.load(u'alt_context.yaml')

        self.assertEqual(
            context.get(u'path'),
            u'alt_context.yaml'
        )

    def test_custom_context_loader(self):

        # custom context loaders are functions that
        # 1) take a path string, and
        # 2) return the context as a dictionary
        def load_json(path):

            with codecs.open(os.path.join(current_app, path)) as infile:
                context = json.load(infile)

            return context

        # customer context loader is applied this way
        g.locales.context_loader = load_json

        # then Locales.load can be called as normal
        context = g.locales.load(u'context.json')

        self.assertEqual(
            context.get(u'path'),
            u'context.json'
        )


class YAMLContextLoadTestCase(WithContext, ContextLoadTests, unittest.TestCase):
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


class JCYLContextLoadTestCase(WithContext, ContextLoadTests, unittest.TestCase):
    """
    Test Strategies

     - each template returns a string containing its path. This way I can easily confirm which template rendered by simply checking the returned string.

    """

    def create_app(self):
        app = Flask(__name__, template_folder=u'templates')
        app.config.from_object(CONFIG)

        app.register_blueprint(blueprint)

        Locales(app)
        Locales.context_loader = json_caching_yaml_loader

        return app
