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

    # Khanh's register and login code to be able to write unit test for my code.
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

    def test_categories(self):
        """ Checks that categories work. """
        """ Khanh helped me write unit-test since I need help writing them for all functions I wrote. """

        rv = self.app.get('/')
        assert b'MyRecipe' in rv.data
        assert b'Recipe of the Day!' in rv.data
        assert b'Search' in rv.data
        assert b'categories' in rv.data

        rv = self.app.get('/categories')
        assert b'30-Min Meals' in rv.data
        assert b'Chinese' in rv.data
        assert b'Mexican' in rv.data
        assert b'Italian' in rv.data
        assert b'American' in rv.data
        assert b'Japanese' in rv.data
        assert b'Indian' in rv.data
        assert b'Greek' in rv.data
        assert b'French' in rv.data

        rv = self.app.get('/view_category?category=30-Min%20Meals')
        assert b'30-Min Meals Recipes' in rv.data

        rv = self.app.get('/view_category?category=Chinese')
        assert b'Chinese Recipes' in rv.data

        rv = self.app.get('/view_category?category=Mexican')
        assert b'Mexican Recipes' in rv.data

        rv = self.app.get('/view_category?category=Italian')
        assert b'Italian Recipes' in rv.data

        rv = self.app.get('/view_category?category=American')
        assert b'American Recipes' in rv.data

        rv = self.app.get('/view_category?category=Japanese')
        assert b'Japanese Recipes' in rv.data

        rv = self.app.get('/view_category?category=indian')
        assert b'indian Recipes' in rv.data

        rv = self.app.get('/view_category?category=Greek')
        assert b'Greek Recipes' in rv.data

        rv = self.app.get('/view_category?category=French')
        assert b'French Recipes' in rv.data

    def test_homePage(self):
        rv = self.app.get('/')
        assert b'MyRecipe' in rv.data
        assert b'Recipe of the Day!' in rv.data
        assert b'Search' in rv.data
        # assert with user login
        assert b'logout' in rv.data
        assert b'account' in rv.data

        # assert without user login
        rv = self.app.get('/logout', follow_redirects=True)
        assert b'MyRecipe' in rv.data
        assert b'Recipe of the Day!' in rv.data
        assert b'Search' in rv.data
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
        assert b'Search' in rv.data
        assert b'logout' in rv.data
        assert b'account' in rv.data

        # logout
        rv = self.app.get('/logout', follow_redirects=True)
        assert b'MyRecipe' in rv.data
        assert b'Recipe of the Day!' in rv.data
        assert b'Search' in rv.data
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
        assert b'Search' in rv.data
        assert b'logout' in rv.data
        assert b'account' in rv.data

        # Log out after successfully login
        rv = self.app.get('/logout', follow_redirects=True)
        assert b'MyRecipe' in rv.data
        assert b'Recipe of the Day!' in rv.data
        assert b'Search' in rv.data
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
        assert b'Search' in rv.data
        assert b'logout' in rv.data
        assert b'account' in rv.data

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
        assert b'Search' in rv.data
        assert b'logout' in rv.data
        assert b'account' in rv.data

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

    def test_recipes(self):
        # Register the user to login
        rv = self.register('khanhta2001', 'khanhta2001@gmail.com', 'testing1234!')
        assert b'Sign in' in rv.data
        assert b'Username or Email' in rv.data
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

    def test_delete_edit(self):
        """ Tests delete function by adding a post and then making sure it is not shown after deleted. """
        """ Also tests edit function by adding a recipe and then making sure it is updated with edits. """

        # register and login test code copied from Khanh since he wrote register and log in functions.
        rv = self.register('khanhta2001', 'khanhta2001@gmail.com', 'testing1234!')
        assert b'Sign in' in rv.data
        assert b'Username or Email' in rv.data
        assert b'Password' in rv.data

        # Correct password
        rv = self.login('khanhta2001', 'testing1234!')
        assert b'MyRecipe' in rv.data
        assert b'Recipe of the Day!' in rv.data
        assert b'logout' in rv.data
        assert b'account' in rv.data

        # Added test recipe
        rv = self.app.get('/create_recipe')
        assert b'title' in rv.data
        assert b'category' in rv.data
        assert b'content' in rv.data
        assert b'Post' in rv.data

        rv = self.app.post('/post_recipe', data=dict(
            title='Title1',
            category='Mexican',
            content='Instructions1'
        ), follow_redirects=True)

        assert b'New recipe successfully posted!' in rv.data
        assert b'MyRecipe' in rv.data
        assert b'Recipe of the Day!' in rv.data

        # Testing edit function
        rv = self.app.get('/view_recipe?recipe_id=1')
        assert b'Title1' in rv.data
        assert b'Mexican' in rv.data
        assert b'Instructions1' in rv.data
        assert b'edit' in rv.data
        assert b'delete' in rv.data

        rv = self.app.get('/edit?id=1')
        assert b'Title1' in rv.data
        assert b'Mexican' in rv.data
        assert b'Instructions1' in rv.data
        assert b'Save' in rv.data

        rv = self.app.post('/edit_recipe', data=dict(
            title='Title Edit',
            category='Chinese',
            content='Instructions Edit',
            id='1'
        ), follow_redirects=True)

        assert b'Recipe Was Successfully Updated!' in rv.data
        assert b'Title Edit' in rv.data
        assert b'Chinese' in rv.data
        assert b'Instructions Edit' in rv.data
        assert b'delete' in rv.data
        assert b'edit' in rv.data

        # Testing delete function
        rv = self.app.post('/delete_recipe', data=dict(
            id='1'
        ), follow_redirects=True)

        assert b'Recipe was successfully deleted!' in rv.data
        assert b'Title Edit' not in rv.data
        assert b'MyRecipe' in rv.data
        assert b'Recipe of the Day!' in rv.data


if __name__ == '__main__':
    unittest.main()
