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

    def test_homePage(self):
        rv = self.app.get('/')
        assert b'MyRecipe' in rv.data
        assert b'Recipe of the Day!' in rv.data
        assert b'Search For Recipes!' in rv.data
        # assert with user login
        assert b'Logout' in rv.data
        assert b'User' in rv.data

        # assert without user login
        rv = self.app.get('/logout', follow_redirects=True)
        assert b'<title>MyRecipe</title>' in rv.data
        assert b'Recipe of the Day!' in rv.data
        assert b'Search For Recipes!' in rv.data
        assert b'Login' in rv.data
        assert b'Register' in rv.data

    def test_authentication(self):
        # Register the user to login
        rv = self.register('khanhta2001', 'khanhta2001@gmail.com', 'testing1234!')
        assert b'Sign in' in rv.data
        assert b'Username or Email' in rv.data
        assert b'Password' in rv.data

        # Correct password
        rv = self.login('khanhta2001', 'testing1234!')
        assert b'MyRecipe' in rv.data
        assert b'Recipe of the Day!' in rv.data
        assert b'Search For Recipes!' in rv.data
        assert b'Logout' in rv.data
        assert b'User' in rv.data

        # logout
        rv = self.app.get('/logout', follow_redirects=True)
        assert b'MyRecipe' in rv.data
        assert b'Recipe of the Day!' in rv.data
        assert b'Search For Recipes!' in rv.data
        assert b'Login' in rv.data
        assert b'Register' in rv.data

        # Wrong password
        rv = self.login('khanhta2001', 'Wrongpassword!')
        assert b'Sign in' in rv.data
        assert b'Username or Email' in rv.data
        assert b'Password' in rv.data
        assert b'Incorrect password' in rv.data

        # Wrong user account
        rv = self.login('WrongUserAccount', 'Wrongpassword!')
        assert b'Sign in' in rv.data
        assert b'Username or Email' in rv.data
        assert b'Password' in rv.data
        assert b'Incorrect username or email' in rv.data

    def test_reset_password(self):
        # register the account
        rv = self.register('khanhta2001', 'khanhta2001@gmail.com', 'testing1234!')
        assert b'Sign in' in rv.data
        assert b'Username or Email' in rv.data
        assert b'Password' in rv.data
        assert b'Forgot Your Password?' in rv.data

        # Reset the password
        rv = self.resetpassword('khanhta2001@gmail.com', 'DifferentPassword!')
        assert b'Sign in' in rv.data
        assert b'Username or Email' in rv.data
        assert b'Password' in rv.data

        # Try login with that new password
        rv = self.login('khanhta2001', 'DifferentPassword!')
        assert b'MyRecipe' in rv.data
        assert b'Recipe of the Day!' in rv.data
        assert b'Search For Recipes!' in rv.data
        assert b'Logout' in rv.data
        assert b'User' in rv.data

        # Log out after successfully login
        rv = self.app.get('/logout', follow_redirects=True)
        assert b'MyRecipe' in rv.data
        assert b'Recipe of the Day!' in rv.data
        assert b'Search For Recipes!' in rv.data
        assert b'Login' in rv.data
        assert b'Register' in rv.data

    def test_useraccount(self):
        # Register an account
        rv = self.register('khanhta2001', 'khanhta2001@gmail.com', 'testing1234!')
        assert b'Sign in' in rv.data
        assert b'Username or Email' in rv.data
        assert b'Password' in rv.data

        # Login to the account
        rv = self.login('khanhta2001', 'testing1234!')
        assert b'MyRecipe' in rv.data
        assert b'Recipe of the Day!' in rv.data
        assert b'Search For Recipes!' in rv.data
        assert b'Logout' in rv.data
        assert b'User' in rv.data

        # Get to the user account
        rv = self.app.get('/user_account')
        assert b'khanhta2001' in rv.data
        assert b'img' in rv.data

    def test_search_save_recipe(self):
        # Register an account
        rv = self.register('khanhta2001', 'khanhta2001@gmail.com', 'testing1234!')
        assert b'Sign in' in rv.data
        assert b'Username or Email' in rv.data
        assert b'Password' in rv.data

        # Login to the account
        rv = self.login('khanhta2001', 'testing1234!')
        assert b'MyRecipe' in rv.data
        assert b'Recipe of the Day!' in rv.data
        assert b'Search For Recipes!' in rv.data
        assert b'Logout' in rv.data
        assert b'User' in rv.data

        rv = self.app.get('/create_recipe')
        assert b'title' in rv.data
        assert b'category' in rv.data
        assert b'content' in rv.data
        assert b'Post' in rv.data

        rv = self.app.post('/post_recipe',
                           data=dict(title='test_title', category='test_category', content='test_content'),
                           follow_redirects=True)
        assert b'New recipe successfully posted!' in rv.data
        assert b'MyRecipe' in rv.data
        assert b'Recipe of the Day!' in rv.data
        # search for a specific recipe
        rv = self.searchResults('test')
        assert b'test_title' in rv.data
        assert b'test_category' in rv.data
        assert b'test_content' in rv.data

        rv = self.app.get('/view_recipe?recipe_id=1')
        assert b'test_title' in rv.data
        assert b'test_category' in rv.data
        assert b'test_content' in rv.data
        assert b'save' in rv.data

        rv = self.app.get('/user_account')
        assert b'khanhta2001' in rv.data
        assert b'img' in rv.data
        assert b'Save your favorite Recipe in here!' in rv.data

        rv = self.app.post('/save_recipe',
                           data=dict(title='test_title', category='test_category', content='test_content'),
                           follow_redirects=True)
        assert b'test_title' in rv.data
        assert b'test_category' in rv.data
        assert b'test_content' in rv.data
        assert b'save' in rv.data

        rv = self.app.get('/user_account')
        assert b'khanhta2001' in rv.data
        assert b'img' in rv.data
        assert b'test_title' in rv.data
        assert b'test_category' in rv.data
        assert b'test_content' in rv.data


if __name__ == '__main__':
    unittest.main()
