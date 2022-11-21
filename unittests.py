import os

from flask import json

import app
import unittest
import tempfile

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

    def login(self, username, password):
        return self.app.post('/login', data=dict(username=username, password=password), follow_redirects=True)

    def resetpassword(self, email, password):
        return self.app.post('/resetpassword', data=dict(email=email, password=password, RetypePassword=password),
                             follow_redirects=True)

    def searchResults(self, searchinput):
        return self.app.post('/search', data=dict(keyword_Search=searchinput), follow_redirects=True)

    def test_recipes(self):
        # Register the user to login
        rv = self.register('khanhta2001', 'khanhta2001@gmail.com', 'testing1234!')
        assert b'Login' in rv.data
        assert b'Username/Email' in rv.data
        assert b'Password' in rv.data

        # Correct password
        rv = self.login('khanhta2001', 'testing1234!')
        assert b'MyRecipe' in rv.data
        assert b'Recipe of the Day!' in rv.data
        assert b'logout' in rv.data
        assert b'account' in rv.data

        # go to the add recipe Page
        rv = self.app.get('/create_recipe')
        assert b'title' in rv.data
        assert b'category' in rv.data
        assert b'content' in rv.data
        assert b'Post' in rv.data
        # post recipe
        rv = self.app.post('/post_recipe', data=dict(
                                            title='test_title',
                                            category='test_category',
                                            content='test_content'
                                        ), follow_redirects=True)
        assert b'New recipe successfully posted!' in rv.data
        assert b'MyRecipe' in rv.data
        assert b'Recipe of the Day!' in rv.data

        rv = self.app.get('/view_recipe?recipe_id=1')
        assert b'test_title' in rv.data
        assert b'test_category' in rv.data
        assert b'test_content' in rv.data
        assert b'Like' in rv.data
        assert b'review' in rv.data
        assert b'No reviews here so far!' in rv.data

        # like recipe
        rv = self.app.post('/like_recipe', data=dict(
                                            action='like',
                                            like_me=1
                                        ), follow_redirects=True)
        assert b'test_title' in rv.data
        assert b'test_category' in rv.data
        assert b'test_content' in rv.data
        assert b'Unlike' in rv.data
        assert b'review' in rv.data
        assert b'No reviews here so far!' in rv.data

        # unlike recipe
        rv = self.app.post('/like_recipe', data=dict(
                                            action='unlike',
                                            unlike_me=1
                                        ), follow_redirects=True)
        assert b'test_title' in rv.data
        assert b'test_category' in rv.data
        assert b'test_content' in rv.data
        assert b'Like' in rv.data
        assert b'review' in rv.data
        assert b'No reviews here so far!' in rv.data

        # go to review recipe page
        rv = self.app.get('/review_recipe?review_me=1')
        assert b'Enter your review here:' in rv.data
        assert b'Post' in rv.data

        # post review
        rv = self.app.post('/post_review', data=dict(
                                            review='test_review',
                                            review_me='1'
                                        ), follow_redirects=True)
        assert b'test_title' in rv.data
        assert b'test_category' in rv.data
        assert b'test_content' in rv.data
        assert b'Like' in rv.data
        assert b'review' in rv.data
        assert b'test_review' in rv.data

        # logout
        rv = self.app.get('/logout', follow_redirects=True)
        assert b'MyRecipe' in rv.data
        assert b'Recipe of the Day!' in rv.data
        assert b'Login' in rv.data
        assert b'Register' in rv.data




if __name__ == '__main__':
    unittest.main()

