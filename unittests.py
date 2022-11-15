import os

from flask import json

import app
import unittest
import tempfile


class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
        app.app.testing = True
        self.app = app.app.test_client()
        with app.app.app_context():
            app.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.app.config['DATABASE'])

    def register(self, username, email, password):
        return self.app.post('/register',
                             data=dict(username=username, Email=email, password=password, RetypePassword=password),
                             follow_redirects=True)

    def login(self,username,password):
        return self.app.post('/login',data=dict(username=username,password=password), follow_redirects=True)

    def test_homePage(self):
        rv = self.app.get('/')
        assert b'<title>MyRecipe</title>' in rv.data
        assert b'Recipe of the Day!' in rv.data
        assert b'Search For Recipes!' in rv.data
        assert b'Login' in rv.data
        assert b'Register' in rv.data

    def test_authentication(self):
        rv = self.register('khanhta2001', 'khanhta2001@gmail.com', 'testing1234!')
        assert b'Login' in rv.data
        assert b'Username/Email' in rv.data
        assert b'Password' in rv.data
        rv = self.login('khanhta2001','testing1234!')
        assert b'<title>MyRecipe</title>' in rv.data
        assert b'Recipe of the Day!' in rv.data
        assert b'Search For Recipes!' in rv.data
        assert b'Logout' in rv.data
        assert b'User' in rv.data
        rv = self.app.get('/logout',follow_redirects=True)
        assert b'<title>MyRecipe</title>' in rv.data
        assert b'Recipe of the Day!' in rv.data
        assert b'Search For Recipes!' in rv.data
        assert b'Login' in rv.data
        assert b'Register' in rv.data


if __name__ == '__main__':
    unittest.main()
