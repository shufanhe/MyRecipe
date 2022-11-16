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
    # recipe of the day should show up according to the date, refering to the covers stored in calendar
    cov = db.execute('SELECT cover FROM calendar WHERE date_today=?', [date.today()])
    cover_today = cov.fetchone()
    id = db.execute('SELECT recipe_id FROM calendar WHERE date_today=?', [date.today()])
    id_today = id.fetchone()
    recipe = db.execute('SELECT title, category, content FROM recipes WHERE id=?', [id_today])
    recipe_today = recipe.fetchone()
    return render_template('HomePage.html', cover=cover_today, recipe=recipe_today)


@app.route('/categories')
def categories():
    db = get_db()
    # redirect to category page
    return render_template('Categories.html')


@app.route('/create_recipe')
def create_recipe():
    if session['user_id'] is None:
        abort(401)
    # redirect to create recipe form
    return render_template('CreateRecipe.html')


@app.route('/post_recipe', methods=['GET', 'POST'])
def post_recipe():
    db = get_db()
    user = session['user_id']
    title = request.form['title']
    category = request.form['category']
    content = request.form['content']
    date_today = str(date.today())
    # take user input and insert into the database
    db.execute('INSERT INTO recipes (user_id, title, category, content, posted_date) VALUES (?, ?, ?, ?, ?)',
               [user, title, category, content, date_today])
    db.commit()
    flash('New recipe successfully posted!')
    return redirect(url_for('HomePage'))


@app.route('/view_recipe')
def view_recipe():
    db = get_db()
    liked = db.execute('SELECT liked FROM like_recipe WHERE user_id=?', [session['user_id']]).fetchone()
    # route if the user clicked on recipe of the day, recipe should show up according to the date
    if ('recipe_of_the_day' in request.args):
        recipe_id_today = db.execute('SELECT recipe_id FROM calendar WHERE date_today=?', [date.today()])
        recipe_today = db.execute('SELECT title, category, content, likes, review FROM recipes WHERE id=?', [recipe_id_today])
        rev = db.execute('SELECT likes, review FROM reviews WHERE recipe_id=?', [recipe_id_today])
        recipe = recipe_today.fetchone()
        reviews = rev.fetchall()
    # route if user clicked on a recipe (not through recipe of the day)
    else:
        rec = db.execute('SELECT id, title, category, content, likes, review FROM recipes WHERE id=?', [request.args.get('recipe_id')])
        rev = db.execute('SELECT review FROM reviews WHERE recipe_id=?', [request.args.get('recipe_id')])
        recipe = rec.fetchone()
        reviews = rev.fetchone()
    return render_template('ViewRecipe.html', recipe=recipe, reviews=reviews, liked=liked)


@app.route('/like_recipe/<int:recipe_id>/<action>', methods=['GET', 'POST'])
#@login_required
def like_recipe(recipe_id, action):
    if session['user_id'] is None:
        abort(401)
    db = get_db()
    current_user = db.execute('SELECT * FROM user WHERE id=?', [session['user_id']]).fetchone()
    recipe_to_like = request.get_json()['to_like']
    # if action == 'like':
    db.execute('UPDATE recipes SET likes=? WHERE recipe_id=?',
                   [request.form['likes'] + 1, request.form['recipe_id']])
    db.execute('UPDATE like_recipe SET liked=? WHERE recipe_id=? AND user_id=?',
                   [1, request.form['recipe_id'], session['user_id']])
    db.session.commit()
    if action == 'unlike':
        db.execute('UPDATE recipes SET likes=? WHERE recipe_id=?',
                   [request.form['likes'] - 1, request.form['recipe_id']])
        db.execute('UPDATE like_recipe SET liked=? WHERE recipe_id=? AND user_id=?',
                   [0, request.form['recipe_id'], session['user_id']])
        db.session.commit()
    #return redirect(url_for('view_recipe'))


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
    cur = db.execute('SELECT * FROM recipes WHERE title LIKE ? OR category LIKE ? OR content LIKE ?', (search_input, search_input, search_input))
    search = cur.fetchall()
    return render_template('SearchResults.html', recipes=search)


@app.route('/register', methods=['GET', 'POST'])
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


@app.route('/login', methods=['GET', 'POST'])
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
    recipe = db.execute('SELECT * FROM recipes WHERE recipe_id = ?', (recipe_id,)).fetchone()
    db.execute("INSERT INTO save_recipe (username, save_recipe) VALUES (?, ?)", (user['username'], recipes['recipe_id']), )
    db.commit()
    return render_template('viewRecipe.html')


@app.route('/user_account')
def user_account():
    db = get_db()
    if session['user_id'] is None:
        abort(401)
    created_recipes = db.execute('SELECT * FROM recipes WHERE user_id=?', [session['user_id']]).fetchall()
    return render_template('user_account.html', created_recipes=created_recipes)
