import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, g, redirect, url_for, render_template, flash, session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, '../database/recipe.db'),
    DEBUG=True,
    SECRET_KEY='development key',
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('../database/schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/')
def HomePage():
    name = None
    return render_template('HomePage.html')


@app.route('/categories')
def categories():
    db = get_db()
    return render_template('Categories.html')


@app.route('/view_recipe')
def view_recipe():
    db = get_db()
    return render_template('ViewRecipe.html')


@app.route('/search', methods=['POST'])
def keyword_search():
    db = get_db()
    search_input = request.form['keyword_Search']
    cur = db.execute("SELECT * FROM recipe WHERE "
                     "title LIKE '%test1%' "
                     "OR category LIKE '%test1%' "
                     "OR content LIKE '%test1%'".format(test1=search_input))
    categories = cur.fetchall()
    return render_template('SearchResults.html')