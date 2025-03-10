import os
from flask import json
import app
import unittest
import tempfile
from flask_mail import Mail
import unittest
import tempfile
from flask_mail import Mail
from datetime import date
from datetime import datetime

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
        app.app.testing = True
        self.mail = Mail(app.app)
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
        return self.app.post('/resetpassword',
                             data=dict(account_email=email, Password=password, RetypePassword=password),
                             follow_redirects=True)

    def searchResults(self, searchinput):
        return self.app.post('/search', data=dict(keyword_Search=searchinput), follow_redirects=True)

    def creating_user_one(self):
        # verifying password (currently do not test OTP code)
        with self.mail.record_messages() as outbox:
            rv = self.register('test1', 'test1@gmail.com', 'testing1234!')
            assert b'Verification' in rv.data
            assert b'verification code' in rv.data
            assert b'Submit' in rv.data
            assert "Hi,\n\nHere is your verification code:" in outbox[0].body
            verification_code = outbox[0].body[37:43]
            rv = self.app.post('/verification', data=dict(OTP=verification_code,
                                                          account_email='test1@gmail.com',
                                                          verification_type='Register'), follow_redirects=True)
            assert b'Sign in' in rv.data
            assert b'Username or Email' in rv.data
            assert b'Password' in rv.data
            assert b'Forgot Your Password' in rv.data
            assert b'New to Food Recipe?'
            assert b'Create an account' in rv.data
        # Correct password
        rv = self.login('test1', 'testing1234!')
        assert b'MyRecipe' in rv.data
        assert b'Recipe of the Day' in rv.data
        assert b'Search' in rv.data
        assert b'logout' in rv.data
        assert b'account' in rv.data

        return rv

    def creating_user_two(self):
        # verifying password (currently do not test OTP code)
        with self.mail.record_messages() as outbox:
            rv = self.register('test2', 'test2@gmail.com', 'testing1234!')
            assert b'Verification' in rv.data
            assert b'verification code' in rv.data
            assert b'Submit' in rv.data
            assert "Hi,\n\nHere is your verification code:" in outbox[0].body
            verification_code = outbox[0].body[37:43]
            rv = self.app.post('/verification', data=dict(OTP=verification_code,
                                                          account_email='test2@gmail.com',
                                                          verification_type='Register'), follow_redirects=True)
            assert b'Sign in' in rv.data
            assert b'Username or Email' in rv.data
            assert b'Password' in rv.data
            assert b'Forgot Your Password' in rv.data
            assert b'New to Food Recipe?'
            assert b'Create an account' in rv.data
        # Correct password
        rv = self.login('test2', 'testing1234!')
        assert b'MyRecipe' in rv.data
        assert b'Recipe of the Day' in rv.data
        assert b'Search' in rv.data
        assert b'logout' in rv.data
        assert b'account' in rv.data

        return rv

    def logout(self):
        rv = self.app.get('/logout', follow_redirects=True)
        assert b'MyRecipe' in rv.data
        assert b'Recipe of the Day' in rv.data
        assert b'Search' in rv.data
        assert b'login' in rv.data
        assert b'register' in rv.data
        return rv

    def test_categories(self):
        """ Checks that categories work. """
        rv = self.app.get('/')
        assert b'MyRecipe' in rv.data
        assert b'Recipe of the Day' in rv.data
        assert b'Search' in rv.data
        assert b'Type in a keyword' in rv.data
        assert b'categories' in rv.data

        rv = self.app.get('/categories')
        assert b'Recipe Categories' in rv.data
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
        assert b'Recipe of the Day' in rv.data
        assert b'Search' in rv.data
        # assert with user login
        assert b'logout' in rv.data
        assert b'account' in rv.data

        # assert without user login
        self.logout()

    def test_login(self):
        # Register the user to login
        rv = self.app.get('/registerPage')
        assert b'Username' in rv.data
        assert b'Email' in rv.data
        assert b'Password' in rv.data
        assert b'Retype Password' in rv.data
        assert b'register' in rv.data

        self.creating_user_one()
        self.logout()

        rv = self.app.get('/loginPage', follow_redirects=True)
        assert b'login' in rv.data
        assert b'Sign in' in rv.data
        assert b'Username or Email' in rv.data
        assert b'Password' in rv.data
        assert b'Forgot Your Password' in rv.data
        assert b'New to Food Recipe?' in rv.data
        assert b'Create an account' in rv.data
        assert b'Need to verify your account?' in rv.data

        # Wrong password
        rv = self.login('test1', 'Wrongpassword!')
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

    def test_register(self):
        # Register the user to login
        rv = self.app.get('/registerPage')
        assert b'Username' in rv.data
        assert b'Email' in rv.data
        assert b'Password' in rv.data
        assert b'Retype Password' in rv.data
        assert b'register' in rv.data

        # register an account without verification
        rv = self.creating_user_one()
        rv = self.logout()

        # try to test to register the account again with the same email and different username
        rv = self.register('different', 'test1@gmail.com', 'testing1234!')
        assert b'test1@gmail.com is already registered' in rv.data

        # try to test to register the account again with different email and same username
        rv = self.register('test1', 'test@gmail.com', 'testing1234!')
        assert b'User test1 is already registered' in rv.data

        # try to test to register the account again with the same email and username
        rv = self.register('test1', 'test1@gmail.com', 'testing1234!')
        assert b'User test1 and test1@gmail.com are already registered' in rv.data

    def test_verification_register(self):
        rv = self.register('test1', 'test1@gmail.com', 'testing1234!')
        rv = self.app.get('/loginPage', follow_redirects=True)
        assert b'Sign in' in rv.data
        assert b'Username or Email' in rv.data
        assert b'Password' in rv.data
        assert b'Forgot Your Password' in rv.data
        assert b'New to Food Recipe?'
        assert b'Create an account' in rv.data
        assert b'Need to verify your account?' in rv.data

        rv = self.login('test1', 'testing1234!')
        assert b'Please verify your account' in rv.data

        rv = self.app.get('/verificationPage', follow_redirects=True)
        assert b'Enter Your Email' in rv.data
        assert b'Email' in rv.data
        assert b'Submit' in rv.data

        with self.mail.record_messages() as outbox:
            rv = self.app.post('/sendingOTP', data=dict(email='test1@gmail.com', verification_type='Verify'),
                               follow_redirects=True)
            assert b'Email Verification' in rv.data
            assert b'Submit' in rv.data
            assert "Hi,\n\nHere is your verification code:" in outbox[0].body
            verification_code = outbox[0].body[37:43]
            rv = self.app.post('/verification', data=dict(OTP=verification_code,
                                                          account_email='test1@gmail.com',
                                                          verification_type='Register'), follow_redirects=True)
            assert b'Sign in' in rv.data
            assert b'Username or Email' in rv.data
            assert b'Password' in rv.data
            assert b'Forgot Your Password' in rv.data
            assert b'New to Food Recipe?'
            assert b'Create an account' in rv.data

            rv = self.login('test1', 'testing1234!')
            assert b'MyRecipe' in rv.data
            assert b'Recipe of the Day' in rv.data
            assert b'Search' in rv.data
            assert b'logout' in rv.data
            assert b'account' in rv.data

    def test_reset_password(self):
        # register the account
        rv = self.creating_user_one()
        rv = self.logout()

        rv = self.app.get('loginPage')
        assert b'Username or Email' in rv.data
        assert b'Password' in rv.data
        assert b'Forgot Your Password' in rv.data

        rv = self.app.get('/verificationPage')
        assert b'Enter Your Email' in rv.data
        assert b'Email' in rv.data
        assert b'Submit' in rv.data

        with self.mail.record_messages() as outbox:
            rv = self.app.post('/sendingOTP', data=dict(email='test1@gmail.com',
                                                        verification_type='ResetPassword'), follow_redirects=True)
            assert b'verification' in rv.data
            assert b'Verification Code' in rv.data
            assert b'Submit' in rv.data
            assert "Hi,\n\nHere is your verification code:" in outbox[0].body

            verification_code = outbox[0].body[28:40]
            rv = self.app.post('/verification', data=dict(verification_code=verification_code, OTP=verification_code,
                                                          account_email='test1@gmail.com',
                                                          verification_type='ResetPassword'), follow_redirects=True)

            rv = self.app.get('/resetpasswordPage', query_string=dict(account_email='test1@gmail.com', verification_type='ResetPassword'),
                              follow_redirects=True)
            assert b'Reset Your Password' in rv.data
            assert b'Password' in rv.data
            assert b'Retype Password' in rv.data
            assert b'Reset Your Password' in rv.data

            # set a new password
            rv = self.resetpassword('test1@gmail.com', 'DifferentPassword!')
            assert b'Sign in' in rv.data
            assert b'Username or Email' in rv.data
            assert b'Password' in rv.data

            # Try login with that new password
            rv = self.login('test1', 'DifferentPassword!')
            assert b'MyRecipe' in rv.data
            assert b'Recipe of the Day' in rv.data
            assert b'Search' in rv.data
            assert b'logout' in rv.data
            assert b'account' in rv.data

            # Log out after successfully login
            self.logout()

    def test_useraccount(self):
        # Register an account
        self.creating_user_one()

        # Get to the user account
        rv = self.app.get('/user_account')
        assert b'test1' in rv.data
        assert b'img' in rv.data
        assert b'Add your created Recipe in here!' in rv.data
        self.logout()

    def test_search_save_recipe(self):
        # Register an account
        self.creating_user_one()

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
        assert b'Recipe of the Day' in rv.data

        rv = self.app.get('/view_recipe?recipe_id=1')
        assert b'test_title' in rv.data
        assert b'test_content' in rv.data
        assert b'Category: test_category' in rv.data
        assert b'Created by' and b'test1' in rv.data
        assert b'edit' in rv.data
        assert b'delete' in rv.data
        assert b'REVIEWS' in rv.data
        assert b'No reviews here so far' in rv.data

        self.logout()

        self.creating_user_two()
        # search for a specific recipe
        rv = self.searchResults('test')
        assert b'test_title' in rv.data

        rv = self.app.get('/view_recipe?recipe_id=1')
        assert b'test_title' in rv.data
        assert b'save' in rv.data

        rv = self.app.post('/save_recipe',
                           data=dict(title='test_title', category='test_category', content='test_content'),
                           follow_redirects=True)
        assert b'test_title' in rv.data
        assert b'Category: test_category' in rv.data
        assert b'test_content' in rv.data
        assert b'save' in rv.data

        rv = self.app.get('/saved_recipes')
        assert b'test_title' in rv.data

        self.logout()

    def test_post_like_review(self):
        # Register the user to login
        self.creating_user_one()

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
        assert b'Recipe of the Day' in rv.data

        rv = self.app.get('/view_recipe?recipe_id=1')
        assert b'test_title' in rv.data
        assert b'test_content' in rv.data
        assert b'Category: test_category' in rv.data
        assert b'Created by' and b'test1' in rv.data
        assert b'like' in rv.data
        assert b'edit' in rv.data
        assert b'delete' in rv.data
        assert b'REVIEWS' in rv.data
        assert b'No reviews here so far!' in rv.data

        # like recipe
        rv = self.app.post('/like_recipe', data=dict(
            action='like',
            like_me=1
        ), follow_redirects=True)
        assert b'test_title' in rv.data
        assert b'Category: test_category' in rv.data
        assert b'Created by' and b'test1' in rv.data
        assert b'test_content' in rv.data
        assert b'unlike' in rv.data
        assert b'review' in rv.data
        assert b'delete' in rv.data
        assert b'edit' in rv.data
        assert b'REVIEWS' in rv.data
        assert b'No reviews here so far!' in rv.data

        # unlike recipe
        rv = self.app.post('/like_recipe', data=dict(
            action='unlike',
            unlike_me=1
        ), follow_redirects=True)
        assert b'test_title' in rv.data
        assert b'Category: test_category' in rv.data
        assert b'Created by' and b'test1' in rv.data
        assert b'test_content' in rv.data
        assert b'like' in rv.data
        assert b'review' in rv.data
        assert b'delete' in rv.data
        assert b'edit' in rv.data
        assert b'REVIEWS' in rv.data
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
        assert b'Category: test_category' in rv.data
        assert b'Created by' and b'test1' in rv.data
        assert b'test_content' in rv.data
        assert b'like' in rv.data
        assert b'review' in rv.data
        assert b'delete' in rv.data
        assert b'edit' in rv.data
        assert b'REVIEWS' in rv.data
        assert b'test_review' in rv.data

        rv = self.app.get('/edit_review?recipe_id=1')
        assert b'test_review' in rv.data
        assert b'Update' in rv.data

        # post edited review
        rv = self.app.post('/post_review_edit', data=dict(
            review='edited review',
            recipe_id='1'
        ), follow_redirects=True)
        assert b'test_title' in rv.data
        assert b'Category: test_category' in rv.data
        assert b'Created by' and b'test1' in rv.data
        assert b'test_content' in rv.data
        assert b'like' in rv.data
        assert b'review' in rv.data
        assert b'delete' in rv.data
        assert b'edit' in rv.data
        assert b'REVIEWS' in rv.data
        assert b'test_review' not in rv.data
        assert b'edited review' in rv.data

        # delete review
        rv = self.app.post('/delete_review', data=dict(
            recipe_id='1'
        ), follow_redirects=True)
        assert b'test_title' in rv.data
        assert b'Category: test_category' in rv.data
        assert b'Created by' and b'test1' in rv.data
        assert b'test_content' in rv.data
        assert b'like' in rv.data
        assert b'review' in rv.data
        assert b'delete' in rv.data
        assert b'edit' in rv.data
        assert b'REVIEWS' in rv.data
        assert b'No reviews here so far!' in rv.data

        # logout
        self.logout()

    def test_notifications(self):
        # Register user 1
        self.creating_user_one()

        # user 1 posts a recipe and logs out
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
        assert b'Recipe of the Day' in rv.data

        rv = self.app.get('/view_recipe?recipe_id=1')
        assert b'test_title' in rv.data
        assert b'test_category' in rv.data
        assert b'test_content' in rv.data


        rv = self.app.get('/view_recipe?recipe_id=1')
        assert b'test_title' in rv.data
        assert b'test_category' in rv.data
        assert b'test_content' in rv.data
        assert b'save' in rv.data

        # review recipe
        rv = self.app.get('/review_recipe?review_me=1')
        assert b'Enter your review here:' in rv.data
        assert b'Post' in rv.data
        rv = self.app.post('/post_review', data=dict(
            review='test_review',
            review_me='1'
        ), follow_redirects=True)
        assert b'test_title' in rv.data
        assert b'test_category' in rv.data
        assert b'test_content' in rv.data
        assert b'like' in rv.data
        assert b'0' in rv.data
        assert b'review' in rv.data
        assert b'test_review' in rv.data

        # like recipe
        rv = self.app.post('/like_recipe', data=dict(
            action='like',
            like_me=1
        ), follow_redirects=True)
        assert b'test_title' in rv.data
        assert b'test_category' in rv.data
        assert b'test_content' in rv.data
        assert b'unlike' in rv.data
        assert b'1' in rv.data
        assert b'review' in rv.data
        assert b'delete' in rv.data
        assert b'edit' in rv.data


        rv = self.app.get('/notifications')
        assert b'<a href="/user_account?author=test1"> test1 </a>' in rv.data
        assert b'liked your' in rv.data
        assert b'<a href="/view_recipe?recipe_id=1">post</a>' in rv.data
        assert b'on' in rv.data
        assert str(date.today()).encode('ASCII') in rv.data
        assert b'at' in rv.data
        assert str(datetime.now().strftime("%H:%M")).encode('ASCII') in rv.data
        assert b'reviewed your' in rv.data
        self.logout()


    def test_delete_edit(self):
        """ Tests delete function by adding a post and then making sure it is not shown after deleted. """
        """ Also tests edit function by adding a recipe and then making sure it is updated with edits. """

        # register and login test code copied from Khanh since he wrote register and log in functions.
        self.creating_user_one()

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
        assert b'Recipe of the Day' in rv.data

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
        assert b'Recipe of the Day' in rv.data

        self.logout()

    def test_seeing_other_user(self):
        self.creating_user_one()
        rv = self.app.post('/post_recipe', data=dict(
            title='Title1',
            category='Mexican',
            content='Instructions1'
        ), follow_redirects=True)

        assert b'New recipe successfully posted!' in rv.data
        assert b'MyRecipe' in rv.data
        assert b'Recipe of the Day' in rv.data

        self.logout()

        self.creating_user_two()

        rv = self.app.get('/view_recipe?recipe_id=1')
        assert b'Title1' in rv.data
        assert b'Category: Mexican' in rv.data
        assert b'Created by' and b'test1' in rv.data
        assert b'Instructions1' in rv.data
        assert b'like' in rv.data
        assert b'review' in rv.data
        assert b'edit' not in rv.data
        assert b'REVIEWS' in rv.data
        assert b'No reviews here so far!' in rv.data

        rv = self.app.get('/user_account', query_string=dict(author='test1'), follow_redirects=True)
        assert b'Name:' and b'test1' in rv.data
        assert b'Email:' and b'test1@gmail.com' in rv.data
        assert b'About Author:' in rv.data
        assert b'follow' in rv.data
        assert b'Created Recipe' in rv.data
        assert b'Title1' in rv.data
        assert b'Author' in rv.data
        assert b'Add your favorite author!' in rv.data

        rv = self.app.post('/follow_author', data=dict(action='follow', author='test1'), follow_redirects=True)
        assert b'Name:' and b'test1' in rv.data
        assert b'Email:' and b'test1@gmail.com' in rv.data
        assert b'About Author:' in rv.data
        assert b'Unfollow' in rv.data
        assert b'Created Recipe' in rv.data
        assert b'Title1' in rv.data
        assert b'Author' in rv.data
        assert b'Add your favorite author!' in rv.data



if __name__ == '__main__':
    unittest.main()
