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

    def test_categories(self):
        rv = self.app.get('/')
        assert b'<title>MyRecipe</title>' in rv.data
        assert b'Recipe of the Day!' in rv.data
        assert b'Search For Recipes!' in rv.data
        assert b'Categories' in rv.data
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

    '''
    def test_delete(self):
        """Tests delete function by adding a post and then making sure it is not shown in main page after deleted."""

        rv = self.app.post('/post_recipe', data=dict(
            title='<Cookies>',
            category='<American>',
            content='<strong>Add milk to the batter</strong> allowed here'
        ), follow_redirects=True)

        assert b'&lt;Cookies&gt;' in rv.data
        assert b'&lt;American&gt' in rv.data
        assert b'<strong>Add milk to the batter</strong> allowed here' in rv.data

        rv = self.app.post('/add', data=dict(
            title='<Orange Chicken>',
            category='<Chinese>',
            content='<strong>Add orange to the chicken</strong> allowed here'
        ), follow_redirects=True)

        assert b'&lt;Orange Chicken&gt;' in rv.data
        assert b'&lt;Chinese&gt' in rv.data
        assert b'<strong>Add orange to the chicken</strong> allowed here' in rv.data

        rv = self.app.post('/delete_recipe', data=dict(
            id=1
        ), follow_redirects=True)

        assert b'&lt;Cookies&gt;' not in rv.data
        assert b'&lt;American&gt' not in rv.data
        assert b'<strong>Add milk to the batter</strong> allowed here' not in rv.data

        assert b'&lt;Orange Chicken&gt;' in rv.data
        assert b'&lt;Chinese&gt' in rv.data
        assert b'<strong>Add orange to the chicken</strong> allowed here' in rv.data

        
        rv = self.app.get('/')
        assert b'&lt;Hello2&gt;' in rv.data
        assert b'&lt;Category2&gt' in rv.data
        assert b'<strong>HTML2</strong> allowed here' in rv.data

        assert b'&lt;Hello1&gt;' not in rv.data
        assert b'&lt;Category1&gt' not in rv.data
        assert b'<strong>HTML1</strong> allowed here' not in rv.data
        '''


if __name__ == '__main__':
    unittest.main()
