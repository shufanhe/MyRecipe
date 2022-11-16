import functools
import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, flash, g, redirect, render_template, request, session, url_for, abort
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date

app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'recipe.db'),
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
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    # make a new admin user
    adminUser()
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


def adminUser():
    """
    We use this so that the us as the developers can mock the website as an administrator
    to test out some specific functions that belong to the administrator only
    """
    db = get_db()
    user = 'admin'
    password = 'verysecurepassword'
    email = 'food@gmail.com'
    db.execute('INSERT INTO user (username, password, email) VALUES (?, ?, ?)', (user, generate_password_hash(password), email))
    db.commit()


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
    # Go to categories to search for other things
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
    """ Shows a list of recipes for whichever category was selected by user. """
    db = get_db()
    cats = request.args.get('category')
    # Gets the category user selected.
    # Query stores the selected recipes by whichever category was selected into cur.
    cur = db.execute('SELECT * FROM recipes WHERE category = ? ORDER BY id DESC', [cats])
    recipes = cur.fetchall()
    # Shows the list of categories calling category_recipes.html
    return render_template('category_recipes.html', recipes=recipes, category=cats)


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


@app.route('/registerPage', methods=['GET'])
def registerPage():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def register():
    # get username, password, RetypePassword and email
    username = request.form['username']
    password = request.form['password']
    retypepassword = request.form['RetypePassword']
    email = request.form['Email']
    db = get_db()
    error = None

    # check if any information is none, otherwise notify the user to enter the required field
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
                return redirect(url_for("loginPage"))
    flash(error)
    return render_template('register.html')


@app.route('/loginPage', methods=['GET'])
def loginPage():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    # get username and password
    # username can be used by both email and user_id
    username = request.form['username']
    password = request.form['password']
    db = get_db()
    error = None

    # check if the user wants to use email or user_id to login
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
    else:
        flash(error)
        return render_template('login.html')


@app.route('/resetpasswordPage', methods=['GET'])
def reset_passwordPage():
    return render_template('resetPassword.html')


@app.route('/resetpassword', methods=['POST'])
def reset_password():
    # get all the required field
    email = request.form['email']
    password = request.form['password']
    retypePassword = request.form['RetypePassword']

    # check if the user enters any information
    if email is None or password is None or retypePassword is None:
        flash('Please enter the missing field')
    if password != retypePassword:
        flash('Please retype your password!')
    else:
        # search in the database to give the user a new password
        db = get_db()
        user = db.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchone()
        # change the password of user
        user['password'] = generate_password_hash(password)
        return redirect(url_for('loginPage'))


@app.route('/logout')
def logout():
    # log out of the website
    session['user_id'] = None
    return redirect(url_for('HomePage'))


@app.route('/save')
def save_recipe():
    if session['user_id'] is None or session['user_id'] == 'admin':
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
    db = get_db()
    if session['user_id'] is None:
        abort(401)
    created_recipes = db.execute('SELECT * FROM recipes WHERE user_id=?', [session['user_id']]).fetchall()
    return render_template('user_account.html', created_recipes=created_recipes)
