# -*- coding: UTF-8 -*- #

import unittest
import os
from flask import Flask, session, g, render_template, Blueprint
from Locales.Locales import Locales
from tests.WithContext import WithContext
from tests.config import CONFIG

# blueprints using a common templates folder
blueprint = Blueprint(u'blueprint', __name__)


class BasicTestCase(WithContext, unittest.TestCase):
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
            u'current_locale.html',
            u'get_tag.html',
            u'get_next_tag.html',
            u'blueprint/template.html'
        ])

    def test_locale_is_correct_type(self):
        """
        locale should be a string
        """
        self.assertIsInstance(g.locales.current, basestring)

    def test_default_locale(self):
        """
        the default locale should be allowed[0]
        """
        self.assertEqual(g.locales.current, CONFIG.LOCALES[0][0])

    def test_set_locale(self):
        """
        I should be able to set the locale
        """
        g.locales.current = u'zh_Hans'
        self.assertEqual(g.locales.current, u'zh_Hans')

    def test_flask_render_template_still_works(self):
        """
        should still be able to use flask.render_template if I want
        :return:
        """
        self.assertEqual(render_template(u'template.html'), u'template.html')

    def test_locales_is_same_as_flask_by_default(self):
        """
        if there are no localed templates available, g.locales.render_template should behave just like flask.render_template

        or

        g.locales.render_template should be a drop-in replacement for flask.render_template
        """

        # explicitly confirm that both functions are equal
        self.assertEqual(
            g.locales.render_template(u'template.html'),
            render_template(u'template.html')
        )

        # explicitly confirm that the result is as expected
        self.assertEqual(
            u'template.html',
            g.locales.render_template(u'template.html')
        )

    def test_locales_can_handle_a_list_of_templates(self):

        self.assertEqual(
            g.locales.render_template([u'_missing_', u'template.html']),
            u'template.html'
        )

    def test_default_is_same_with_blueprints_too(self):
        """
        if there are no localed templates available, g.locales.render_template should behave just like flask.render_template

        or

        g.locales.render_template should be a drop-in replacement for flask.render_template
        """

        # explicitly confirm that both functions are equal
        self.assertEqual(
            g.locales.render_template(u'blueprint/template.html'),
            render_template(u'blueprint/template.html')
        )

        # explicitly confirm that the result is as expected
        self.assertEqual(
            u'blueprint/template.html',
            g.locales.render_template(u'blueprint/template.html')
        )

    def test_template_global_current_locale(self):

        g.locales.current = u'en'
        self.assertEqual(u'en', g.locales.render_template(u'current_locale.html'))

        g.locales.current = u'zh_Hans'
        self.assertEqual(u'zh_Hans', g.locales.render_template(u'current_locale.html'))

    def test_template_global_get_tag(self):

        g.locales.current = u'en'
        self.assertEqual(u'EN', g.locales.render_template(u'get_tag.html'))

        g.locales.current = u'zh_Hans'
        self.assertEqual(u'中文', g.locales.render_template(u'get_tag.html'))

    def test_template_global_get_tag(self):

        g.locales.current = u'en'
        self.assertEqual(u'中文', g.locales.render_template(u'get_next_tag.html'))

        g.locales.current = u'zh_Hans'
        self.assertEqual(u'EN', g.locales.render_template(u'get_next_tag.html'))

    def test_localify_path(self):

        g.locales.current = u'en'
        self.assertEqual(u'en/template.html', g.locales._localify_path(u'template.html'))

        g.locales.current = u'zh_Hans'
        self.assertEqual(u'zh_Hans/context.yaml', g.locales._localify_path(u'context.yaml'))

    def test_localify_path_with_blueprints(self):

        g.locales.current = u'en'
        self.assertEqual(u'blueprint/en/template.html', g.locales._localify_path(u'blueprint/template.html'))

        g.locales.current = u'zh_Hans'
        self.assertEqual(u'blueprint/zh_Hans/context.yaml', g.locales._localify_path(u'blueprint/context.yaml'))
