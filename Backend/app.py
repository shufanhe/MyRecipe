import functools
import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, flash, g, redirect, render_template, request, session, url_for, abort
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
                     "title LIKE '%{search}%' "
                     "OR category LIKE '%{search}%' "
                     "OR content LIKE '%{search}%'".format(search=search_input))
    search = cur.fetchall()
    return render_template('SearchResults.html')


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        RetypePassword = request.form['RetypePassword']
        email = request.form['Email']
        db = get_db()
        error = None
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not RetypePassword:
            error = 'Please retype your password.'
        elif not email:
            error = 'Email is required.'

        if error is None:
            if password != RetypePassword:
                error = 'Please enter your password correctly.'
            else:
                try:
                    db.execute("INSERT INTO user (username, password,email) VALUES (?, ?,?)",
                               (username, generate_password_hash(password), email),)
                    db.commit()
                except db.IntegrityError:
                    error = f"User {username} is already registered."
                else:
                    return redirect(url_for("login"))
        flash(error)

    return render_template('register.html')


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        if "@" in username:
            user = db.execute('SELECT * FROM user WHERE email = ?', (username,)).fetchone()
        else:
            user = db.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()
        if user is None:
            error = 'Incorrect username or email.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        if error is None:
            session.clear()
            session['user_id'] = user['username']
            return redirect(url_for('HomePage'))
        flash(error)
    return render_template('login.html')


@app.route('/resetpassword', methods=['GET', 'POST'])
def forget_password():
    if request.method == 'POST':
        flash('Please check your email for the OTP code')
        return redirect(url_for('login'))
    return render_template('forgotPassword.html')


@app.route('/logout')
def logout():
    session['user_id'] = None
    return redirect(url_for('HomePage'))


@app.route('/save')
def save_recipe():
    if session['user_id'] is None:
        abort(401)
    recipe_id = request.get_json()['recipe_id']
    db = get_db()
    user = db.execute('SELECT * FROM user WHERE username = ?', (session['user_id'],)).fetchone()
    recipe = db.execute('SELECT * FROM recipe WHERE id = ?', (recipe_id,)).fetchone()
    db.execute("INSERT INTO save_recipe (username, save_recipe) VALUES (?, ?)", (user['username'], recipe['id']), )
    db.commit()
    return render_template('viewRecipe.html')


@app.route('/user_account')
def user_account():
    if session['user_id'] is None:
        abort(401)
    return render_template('user_account.html')
