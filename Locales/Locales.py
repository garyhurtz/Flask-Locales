# -*- coding: UTF-8 -*- #

from flask import g, session, render_template, request, current_app
import os
from Loaders import yaml_loader


class Locales(object):
    """
    Implements locale-related functions.
    """

    context_loader = yaml_loader
    context_folder = u'context'

    def __init__(self, app=None):

        # placeholders
        self._allowed = []
        self._tags = []
        self.tag_map = {}

        self._current = None
        self._next = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app):

        app.before_request(self.before_request)

        locales = app.config.get(u'LOCALES', [(u'en', u'EN')])

        self._allowed = [l[0] for l in locales]
        self._tags = [l[1] for l in locales]

        self.tag_map = dict(zip(self._allowed, self._tags))

    def before_request(self):

        # make Locales available on g
        g.locales = self

        # template globals
        current_app.jinja_env.globals[u'current_locale'] = self.get_current
        current_app.jinja_env.globals[u'next_locale_tag'] = self.get_next_tag

        # template filters
        current_app.jinja_env.filters[u'tag'] = self.tag

    def get_current(self):
        """
        execute the current_locale global

        :return: the current locale
        """
        return self.current

    def tag(self, locale):
        """
        execute the tag filter

        :param locale: the locale to convert
        :return: the tag corresponding to locale
        """
        return self.tag_map.get(locale)

    def get_next_tag(self):
        """
        Return the tag for the next locale

        :return: the tag corresponding to the next locale
        """
        return self.tag_map.get(self.next())

    @property
    def default(self):
        """
        Return the default locale

        :return: the default locale
        """
        return self._allowed[0]

    @property
    def current(self):
        """
        Return the current locale

        :return: the current locale
        """

        if self._current is None:

            # get the locale from the session
            locale = session.get(u'locale', None)

            # if locale has not been defined, get best match from the browser
            if locale is None:
                locale = request.accept_languages.best_match(self._allowed)

            # if I still cant figure it out, use the default
            if locale is None:
                locale = self.default

            # set the current locale
            self.set(locale)

        return self._current

    def next(self):
        """
        Return the next locale

        Useful for applications with a single "next locale" button.

        :return: the next locale
        """
        # get the index of the current locale
        idx = self._allowed.index(self.current)

        try:
            # get the locale at the next index
            next_locale = self._allowed[idx + 1]

        except IndexError:
            # an overflow occurred, the next idx is 0
            next_locale = self._allowed[0]

        return next_locale

    def toggle(self):
        """
        Toggle the locale

        Useful for application with a single "next locale" button.

        :return: None
        """
        self.set(self.next())

    def set(self, locale):
        """
        Set a specific locale.

        :param locale: the desired locale
        :return: None
        """
        session[u'locale'] = locale
        self._current = locale

    def render_template(self, template_name_or_list, context=None, **ctx):
        """
        Render localed templates.

        :param template_name_or_list: identical to Flask.render_template
        :param context: name of file containing localized context information or None
        :param ctx: - identical to Flask.render_template
        :return: the rendered template
        """

        if isinstance(template_name_or_list, basestring):
            template_name_or_list = [template_name_or_list]

        localified = [self._localify_path(name) for name in template_name_or_list] + template_name_or_list

        # if in debug and context is not None
        # render the static context
        if context is not None:
            ctx.update(self.load(context))

        # now handle any localized content within ctx
        ctx = self._localify_context(**ctx)

        return render_template(localified, **ctx)

    def _localify_path(self, path):
        """
        Takes a template or context path, and returns the path to the
        corresponding localized file (if it exists) according to the current locale.

        Example 1:
        'template.html' --> '<loc>/template.html'

        Example 2:
        'blueprint/context.yaml' --> 'blueprint/<loc>/context.yaml'

        :param path: the desired path
        :return: the localized path
        """

        # if the requested path is at the root level, look for locales under the root
        if u'/' not in path:
            return os.path.join(g.locales.current, path)

        # if a pre-localed path was passed, just return it

        # - if using blueprints:
        if u'/{0}/'.format(g.locales.current) in path:
            return path

        # - if not using blueprints
        if path.startswith(u'{0}/'.format(g.locales.current)):
            return path

        # insert the locale into the path
        path_list = path.rsplit(u'/', 1)
        path_list.insert(1, g.locales.current)

        return os.sep.join(path_list)

    def _localify_context(self, **context):
        """
        Return the context with any localed content promoted to the top level

        Example 0: Just pass the locale you want to render
        {greeting: Hello} --> {greeting: Hello}

        Example 1: Pass multiple locales, but use the right one
        {en: {greeting: Hello}, zh_Hans: {greeting: 你好}} --> {greeting: Hello, en: {greeting: Hello}, zh_Hans: {greeting: 你好}}

        :param context: the context to render
        :return: the localized context
        """

        if g.locales.current in context:
            context.update(context.get(g.locales.current))

        return context

    def load(self, path):
        """
        Load context from path

        :param path: the path to load
        :return: the context
        """
        # build a sequence of paths to try
        attempts = (self._localify_path(path), path)

        for attempt in attempts:
            try:
                _path = os.path.join(
                    current_app.root_path,
                    self.context_folder,
                    attempt
                )

                return self.context_loader(_path)

            except IOError:
                pass

            except OSError:
                pass

        # if I haven't found the context yet, look for a common context
        # this time I want to raise IOError if I don't find the file
        context = self.context_loader(
            os.path.join(
                current_app.root_path,
                path
            )
        )

        return context
