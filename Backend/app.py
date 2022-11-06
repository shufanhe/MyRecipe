import functools
import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, flash, g, redirect, render_template, request, session, url_for, abort
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date
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
    db = get_db()
    cov = db.execute('SELECT cover FROM calendar WHERE date_today=?', [date.today()])
    cover_today = cov.fetchone()
    return render_template('HomePage.html', cover=cover_today)


@app.route('/categories')
def categories():
    db = get_db()
    return render_template('Categories.html')


@app.route('/create_recipe')
def create_recipe():
    db = get_db()
    return render_template('CreateRecipe.html')


@app.route('/post', methods=['POST'])
def post_recipe():
    db = get_db()
    db.execute('INSERT INTO recipes (title, category, content) VALUES (?, ?, ?)',
               [request.form['title'], request.form['category'], request.form['content']])
    db.commit()
    flash('New recipe successfully posted!')
    return redirect(url_for('HomePage'))


@app.route('/view_recipe')
def view_recipe():
    db = get_db()
    if ('recipe_of_the_day' in request.args):
        recipe_id_today = db.execute('SELECT recipe_id FROM recipes WHERE date_today=?', [date.today()])
        recipe_today = db.execute('SELECT title, category, content FROM recipes WHERE id=?', [recipe_id_today])
        recipe = recipe_today.fetchone()
    else:
        post_id = request.args.get('clicked')
        rec = db.execute('SELECT title, category, content FROM recipes WHERE id=?', [post_id])
        recipe = rec.fetchone()
    return render_template('ViewRecipe.html', recipe=recipe)


@app.route('/view_category')
def view_category():
    db = get_db()
    cats = request.args.get('category')
    cur = db.execute('SELECT id, title, content, category FROM recipes WHERE category = ? ORDER BY id DESC',
                     [cats])
    category = cur.fetchall()
    return render_template('category_recipes.html', category=category)


@app.route('/search', methods=['POST'])
def keyword_search():
    db = get_db()
    search_input = request.form['keyword_Search']
    cur = db.execute("SELECT * FROM recipes WHERE "
                     "title LIKE '%test1%' "
                     "OR category LIKE '%test1%' "
                     "OR content LIKE '%test1%'".format(test1=search_input))
    categories = cur.fetchall()
    return render_template('SearchResults.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",(username, generate_password_hash(password)),)
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("login"))
        flash(error)

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('HomePage'))
        flash(error)
    return render_template('login.html')


@app.route('/logout')
def logout():
    session['user_id'] = None
    return redirect(url_for('HomePage'))
