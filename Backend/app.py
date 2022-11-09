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
    # Connect with the homepage
    db = get_db()
    # Get from db what date is today
    cov = db.execute('SELECT cover FROM calendar WHERE date_today=?', [date.today()])
    cover_today = cov.fetchone()
    return render_template('HomePage.html', cover=cover_today)


@app.route('/categories')
def categories():
    # Go to categories to search for other things
    db = get_db()
    return render_template('Categories.html')


@app.route('/create_recipe')
def create_recipe():
    # create recipe and add it to the database
    return render_template('CreateRecipe.html')


@app.route('/post', methods=['POST'])
def post_recipe():
    db = get_db()
    # push recipe created
    db.execute('INSERT INTO recipes (title, category, content) VALUES (?, ?, ?)',
               [request.form['title'], request.form['category'], request.form['content']])
    db.commit()
    flash('New recipe successfully posted!')
    return redirect(url_for('HomePage'))


@app.route('/view_recipe')
def view_recipe():
    db = get_db()
    # view a specific recipe or only recipe of the day
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
    """ Shows a list of recipes for whichever category was selected by user. """

    db = get_db()
    cats = request.args.get('category')  # Gets the category user selected.

    # Query stores the selected recipes by whichever category was selected into cur.
    cur = db.execute('SELECT id, title, content, category FROM recipes WHERE category = ? ORDER BY id DESC',
                     [cats])
    category = cur.fetchall()

    # Shows the list of categories calling category_recipes.html
    return render_template('category_recipes.html', category=category)


@app.route('/search', methods=['POST'])
def keyword_search():
    db = get_db()
    # search word, sentence
    search_input = "%" + request.form['keyword_Search'] + "%"

    # search in the database if there is anything like or similar to that
    cur = db.execute('SELECT * FROM recipes WHERE title LIKE ? OR category LIKE ? OR content LIKE ?',
                     (search_input, search_input, search_input))
    search = cur.fetchall()
    return render_template('SearchResults.html', recipes=search)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # get username, password, RetypePassword and email
        username = request.form['username']
        password = request.form['password']
        retypepassword = request.form['RetypePassword']
        email = request.form['Email']
        db = get_db()
        error = None

        # check if any is none
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not retypepassword:
            error = 'Please retype your password.'
        elif not email:
            error = 'Email is required.'

        if error is None:
            if password != retypepassword:
                # if the password is not the same as RetypePassword then return error
                if password != retypepassword:
                    error = 'Please enter your password correctly.'
                else:
                    # try to register the username, if not return error that user_id already registered
                    try:
                        db.execute("INSERT INTO user (username, password,email) VALUES (?, ?,?)",
                                   (username, generate_password_hash(password), email), )
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
        # get username and password
        # username can be used by both email and user_id
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # check if there the username is email or just user_id
        if "@" in username:
            user = db.execute('SELECT * FROM user WHERE email = ?', (username,)).fetchone()
        else:
            user = db.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()

        # check to see if the username is empty or not
        if username is None:
            error = 'Incorrect username or email.'

        # check to see if the password is correct or not
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        if error is None:
            session.clear()
            # login with session being username
            session['user_id'] = user['username']
            return redirect(url_for('HomePage'))
        flash(error)
    return render_template('login.html')


@app.route('/resetpassword', methods=['GET','POST'])
def reset_password():
    if request.method == 'POST':
        # get all the required field
        email = request.form['email']
        password = request.form['password']
        retypePassword = request.form['RetypePassword']
        if email is None or password is None or retypePassword is None:
            flash('Please enter the missing field')
        if password != retypePassword:
            flash('Please retype your password!')
        else:
            # search in the database
            db = get_db()
            user = db.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchone()
            # change the password of user
            user['password'] = generate_password_hash(password)
            return redirect(url_for('login'))
    return render_template('resetPassword.html')


@app.route('/logout')
def logout():
    # log out of the website
    session['user_id'] = None
    return redirect(url_for('HomePage'))


@app.route('/save')
def save_recipe():
    if session['user_id'] is None:
        # abort if there is the user is not logged in
        abort(401)
    # save recipe to user_id in the database
    recipe_id = request.get_json()['recipe_id']
    db = get_db()

    # get the user database
    user = db.execute('SELECT * FROM user WHERE username = ?', (session['user_id'],)).fetchone()

    # get the recipe database
    recipe = db.execute('SELECT * FROM recipe WHERE id = ?', (recipe_id,)).fetchone()

    # save the recipe in the save_recipe database
    db.execute("INSERT INTO save_recipe (username, save_recipe) VALUES (?, ?)", (user['username'], recipe['id']), )
    db.commit()
    return render_template('viewRecipe.html')


@app.route('/user_account')
def user_account():
    if session['user_id'] is None:
        abort(401)
    return render_template('user_account.html')
