# -*- coding: UTF-8 -*- #


class WithContext(object):
    """
    Mixin to add context to tests

    This mixin must be applied before unittest.TestClient:

        class SomeTestCase(WithContext, unittest.TestCase):
            ...

    Tests must:
     - have a create_app() method that sets up the app

    Tests may:
     - define a beforeEach() method which replaces unittest.setUp
     - define a afterEach() method which replaces unittest.tearDown

    A few instance properties are created:

    self.app - the app
    self.client - the test client
    self.ctx - the test context

    """

    def create_app(self):
        raise NotImplemented(u'You need to override create_app')

    def beforeEach(self):
        """
        Override in testcase

        Runs with context
        :return:
        """
        pass

    def _beforeEach(self):
        self.app.preprocess_request()
        self.beforeEach()

    def afterEach(self):
        """
        Override in testcase

        Runs with context
        :return:
        """
        pass

    def setUp(self):
        self.app = self.create_app()

        self.client = self.app.test_client()
        self.ctx = self.app.test_request_context()

        # push the context to the stack
        self.ctx.push()

        self._beforeEach()

    def tearDown(self):
        self.afterEach()

        # pop the context from the stack
        self.ctx.pop()
