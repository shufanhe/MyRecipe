import functools
import os
import random
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date
from datetime import datetime

app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'recipe.db'),
    DEBUG=True,
    SECRET_KEY='development key',
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'testdevappfood@gmail.com'
app.config['MAIL_PASSWORD'] = 'ozxbpxdxfkumqodf'
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = 'testdevappfood@gmail.com'

mail = Mail(app)


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
    db.execute('INSERT INTO user (username, password, email,verified,OTP_code) VALUES (?,?,?,?,?)',
               (user, generate_password_hash(password), email, 'verified', 0))
    db.commit()


def recipe():
    db = get_db()


@app.route('/')
def HomePage():
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
    if session['user_id'] is None or session['user_id'] == 'admin':
        flash('You are not allowed to create a recipe')
        return redirect(url_for('HomePage'))
    # redirect to create recipe form
    return render_template('CreateRecipe.html')


@app.route('/post_recipe', methods=['POST'])
def post_recipe():
    if session['user_id'] == 'admin' or session['user_id'] is None:
        flash('Make an account to be able to add a recipe!')
        return redirect(url_for('HomePage'))
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
    current_user = session['user_id']
    cur = db.execute('SELECT COUNT(1) FROM like_recipe WHERE user_id=? AND recipe_id=?',
                     [session['user_id'], request.args.get('recipe_id')])
    whether_liked = cur.fetchone()[0]
    # route if the user clicked on recipe of the day, recipe should show up according to the date
    if 'recipe_of_the_day' in request.args:
        recipe_id_today = db.execute('SELECT recipe_id FROM calendar WHERE date_today=?', [date.today()])
        recipe_today = db.execute('SELECT title, category, content, likes, review FROM recipes WHERE id=?',
                                  [recipe_id_today])
        rev = db.execute('SELECT likes, review FROM reviews WHERE recipe_id=?', [recipe_id_today])
        recipe = recipe_today.fetchone()
        reviews = rev.fetchall()
        return render_template('ViewRecipe.html', recipe=recipe, reviews=reviews, liked=whether_liked,
                               current_user=current_user)
    # route if user clicked on a recipe (not through recipe of the day)
    else:
        cur2 = db.execute('SELECT COUNT(1) FROM recipes WHERE id=?',
                          [request.args.get('recipe_id')])
        whether_exist = cur2.fetchone()[0]
        if whether_exist == 0:
            flash('The recipe has been deleted.')
            return redirect(url_for('notifications'))
        else:
            rec = db.execute('SELECT id, title, category, content, likes, user_id FROM recipes WHERE id=?',
                             [request.args.get('recipe_id')])
            recipe = rec.fetchone()
            rev = db.execute('SELECT recipe_id, user_id, review FROM reviews WHERE recipe_id=?',
                             [request.args.get('recipe_id')])
            reviews = rev.fetchall()
            return render_template('ViewRecipe.html', recipe=recipe, reviews=reviews, liked=whether_liked,
                                   current_user=current_user)


@app.route('/like_recipe', methods=['POST'])
def like_recipe():
    db = get_db()
    # current_user = db.execute('SELECT * FROM user WHERE id=?', [session['user_id']]).fetchone()
    # recipe_liked = request.get_json()['to_like']
    # recipe_to_like = request.form['like_me']
    # print("ID", recipe_to_like)
    action = request.form['action']
    if action == 'like':
        recipe_id = request.form['like_me']
        if session['user_id'] is None:
            flash('You need to login to like recipe')
            return redirect(url_for('view_recipe', recipe_id=recipe_id))
        cur = db.execute('SELECT user_id FROM recipes WHERE id=?', [recipe_id])
        to_user = cur.fetchone()[0]
        db.execute('UPDATE recipes SET likes=likes+1 WHERE id=?', [recipe_id])
        db.execute('INSERT INTO like_recipe (recipe_id, user_id) VALUES (?, ?)', [recipe_id, session['user_id']])
        current_date = date.today()
        current_time = datetime.now().strftime("%H:%M")
        db.execute(
            'INSERT INTO notifications (recipe_id, to_user, from_user, action_type, action_date, action_time) VALUES (?, ?, ?, ?, ?, ?)',
            [recipe_id, to_user, session['user_id'], 'liked', current_date, current_time])
        db.commit()
    if action == 'unlike':
        recipe_id = request.form['unlike_me']
        # just check if row is in table, if no than have not liked
        # don't need to request action from frontend
        db.execute('UPDATE recipes SET likes=likes-1 WHERE id=?', [recipe_id])
        db.execute('DELETE FROM like_recipe WHERE recipe_id=? AND user_id=?', [recipe_id, session['user_id']])
        db.commit()
    return redirect(url_for('view_recipe', recipe_id=recipe_id))


@app.route('/review_recipe', methods=['GET'])
def review_recipe():
    db = get_db()
    recipe_id = request.args.get('review_me')
    if session['user_id'] is None:
        flash('You need to login to review')
        return redirect(url_for('view_recipe', recipe_id=recipe_id))
    cur1 = db.execute('SELECT * FROM reviews WHERE recipe_id=? AND user_id=?', [recipe_id, session['user_id']])
    if cur1.fetchone() is not None:
        flash('You have already reviewed this recipe')
        return redirect(url_for('view_recipe', recipe_id=recipe_id))
    else:
        cur2 = db.execute('SELECT * FROM recipes WHERE id=?', [recipe_id])
        recipe = cur2.fetchone()
        return render_template('review_recipe.html', recipe=recipe)


@app.route('/post_review', methods=['POST'])
def post_review():
    db = get_db()
    recipe_to_review = int(request.form['review_me'])
    review = request.form['review']
    db.execute('INSERT INTO reviews (recipe_id, user_id, review) VALUES (?, ?, ?)',
               [recipe_to_review, session['user_id'], review])
    cur = db.execute('SELECT user_id FROM recipes WHERE id=?', [recipe_to_review])
    to_user = cur.fetchone()[0]
    current_date = date.today()
    current_time = datetime.now().strftime("%H:%M")
    db.execute(
        'INSERT INTO notifications (recipe_id, to_user, from_user, action_type, action_date, action_time) VALUES (?, ?, ?, ?, ?, ?)',
        [recipe_to_review, to_user, session['user_id'], 'reviewed', current_date, current_time])
    db.commit()
    cur = db.execute('SELECT * FROM reviews WHERE recipe_id=?', [recipe_to_review])
    reviews = cur.fetchall()
    return redirect(url_for('view_recipe', reviews=reviews, recipe_id=recipe_to_review))


@app.route('/delete_review', methods=['POST'])
def delete_review():
    db = get_db()
    recipe_id = request.form['recipe_id']
    db.execute('DELETE FROM reviews WHERE user_id=? AND recipe_id=?', [session['user_id'], recipe_id])
    db.commit()
    flash("Review was successfully deleted!")
    return redirect(url_for('view_recipe', recipe_id=recipe_id))


@app.route('/edit_review', methods=['GET'])
def edit_review():
    db = get_db()
    recipe_id = request.args.get('recipe_id')
    cur = db.execute('SELECT * FROM reviews WHERE user_id=? AND recipe_id=?', [session['user_id'], recipe_id])
    review = cur.fetchone()
    return render_template('edit_review.html', review=review)


@app.route('/post_review_edit', methods=['POST'])
def post_review_edit():
    recipe_id = request.form['recipe_id']
    db = get_db()
    db.execute('UPDATE reviews SET review=? WHERE user_id=? AND recipe_id=?',
               [request.form['review'], session['user_id'], recipe_id])
    db.commit()
    flash('Review Was Successfully Updated!')
    return redirect(url_for('view_recipe', recipe_id=recipe_id))


@app.route('/view_category', methods=['GET'])
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
    elif '@' not in email or '.' not in email:
        error = 'Please enter the correct email domain'
    elif password != retypepassword:
        error = 'Please enter your password correctly.'
    if error is None:
        # Check username and email to see if they are already registered
        user = db.execute('SELECT * FROM user WHERE username = ? and email != ?', [username, email])
        user = user.fetchall()
        check_email = db.execute('SELECT * FROM user where email = ? and username != ?', [email, username])
        check_email = check_email.fetchall()
        registration = db.execute('SELECT * FROM user WHERE username = ? AND email = ?', [username, email])
        registration = registration.fetchone()
        if len(user) == 0 and len(check_email) == 0 and registration is None:
            msg = Message("Email registration for Food Recipe Account", recipients=[email])
            OTP = random.randrange(100000, 999999)
            msg.body = "Hi,\n\nHere is your verification code:\n" + str(
                OTP) + "\n\n" + "Thank you,\nFood Recipe Admin team"
            mail.send(msg)
            flash('Please check your email for verification code')
            verification_type = "Register"
            db.execute("INSERT INTO user (username,password,email,verified,OTP_code) VALUES (?,?,?,?,?)",
                       (username, generate_password_hash(password), email.lower(), 'unverified',
                        generate_password_hash(str(OTP))))
            db.commit()
            return render_template('verificationOTP.html', verification_code=OTP, account_email=email,
                                   verification_type=verification_type)
        elif registration is not None:
            if registration['verified'] == 'unverified':
                msg = Message("Email registration for Food Recipe Account", recipients=[email])
                OTP = random.randrange(100000, 999999)
                msg.body = "Hi,\n\nHere is your verification code:\n" + str(
                    OTP) + "\n\n" + "Thank you,\nFood Recipe Admin team"
                mail.send(msg)
                flash('Please check your email for verification code again')
                verification_type = "Register"
                db.execute('UPDATE user SET OTP_code = ? WHERE email = ?', (generate_password_hash(str(OTP)), email))
                db.commit()
                return render_template('verificationOTP.html', account_email=email, verification_type=verification_type)
            else:
                error = f"User {username} and {email} are already registered"
        else:
            if len(check_email) != 0:
                error = f"{email} is already registered"
            elif len(user) != 0:
                error = f"User {username} is already registered"
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
        user = db.execute('SELECT * FROM user WHERE email = ?', [username.lower()])
        user = user.fetchone()
    else:
        user = db.execute('SELECT * FROM user WHERE username = ?', [username])
        user = user.fetchone()
    # check to see if the username is empty or not
    if user is None or username is None:
        error = 'Incorrect username or email'

    # check to see if the password is correct or not
    elif not check_password_hash(user['password'], password):
        error = 'Incorrect password'
    elif user['verified'] == 'unverified':
        error = 'Please verify your account by registering again.'
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
    email = request.args.get('account_email')
    verification_type = request.args.get('verification_type')
    return render_template('resetPassword.html', account_email=email,
                           verification_type=verification_type)


@app.route('/resetpassword', methods=['POST'])
def reset_password():
    # get all the required field
    password = request.form['Password']
    retypePassword = request.form['RetypePassword']
    email = request.form['account_email']
    # check if the user enters any information
    if password is None or retypePassword is None:
        flash('Please enter the missing field')
        return redirect(url_for('reset_passwordPage'))
    elif password != retypePassword:
        flash('Please retype your password!')
        return redirect(url_for('reset_passwordPage'))
    else:
        # search in the database to give the user a new password
        db = get_db()
        db.execute('UPDATE user SET password = ? WHERE email = ?', (generate_password_hash(password), email))
        db.commit()
        # change the password of user
        flash('Your password has been reset. Please log in with your new password!')
        return redirect(url_for('loginPage'))


@app.route('/verificationPage', methods=['GET'])
def verificationPage():
    verification_type = request.args.get('verification_type')
    return render_template('verificationPage.html', verification_type=verification_type)


@app.route('/verification', methods=['POST'])
def verification():
    db = get_db()
    account_email = request.form['account_email']
    verification_type = request.form['verification_type']
    OTP = request.form['OTP']
    user = db.execute("SELECT * FROM user WHERE email == ?", [account_email])
    user = user.fetchone()
    verification_code = user['OTP_code']
    if not check_password_hash(verification_code, OTP):
        flash('Please enter the correct verification code')
        return render_template('verificationOTP.html', account_email=account_email, verification_type=verification_type)
    else:
        if verification_type == 'Register':
            db = get_db()
            db.execute('UPDATE user SET verified = ? WHERE email = ?', ['verified', account_email])
            db.commit()
            flash('Your account has been verified. You can log in now')
            return redirect(url_for('loginPage'))
        else:
            return redirect(url_for('reset_passwordPage', account_email=account_email))


@app.route('/sendingOTP', methods=['POST'])
def sendingOTP():
    email = request.form['email']
    verification_type = request.form['verification_type']
    db = get_db()
    user = db.execute('SELECT * FROM user WHERE email = ?', [email])
    user = user.fetchone()
    if user is None:
        flash('There is no account registered under that email')
        return redirect(url_for('verificationPage'))
    msg = Message("Email Verification for Food Recipe Account", recipients=[email])
    OTP = random.randrange(100000, 999999)
    msg.body = "Hi,\n\nHere is your verification code:\n" + str(OTP) + "\n\n" + "Thank you,\nFood Recipe Admin team"
    mail.send(msg)
    flash('Please check your email for OTP code')
    db.execute('UPDATE user SET OTP_code = ? WHERE email = ?', [generate_password_hash(str(OTP)), email])
    db.commit()
    return render_template('verificationOTP.html', account_email=email, verification_type=verification_type)


@app.route('/logout')
def logout():
    # log out of the website
    session['user_id'] = None
    return redirect(url_for('HomePage'))


@app.route('/save_recipe', methods=['POST'])
def save_recipe():
    # save recipe to user_id in the database
    title = request.form['title']
    content = request.form['content']
    category = request.form['category']
    db = get_db()

    # get the recipe database
    recipe_element = db.execute('SELECT * FROM recipes WHERE title = ? AND content = ? AND category = ?',
                                (title, content, category)).fetchone()
    # save the recipe in the save_recipe database
    check_save = db.execute(
        'SELECT * FROM save_recipe WHERE username = ? AND title = ? AND content = ? AND category = ?',
        (session['user_id'], title, content, category)).fetchone()

    if session['user_id'] is None or session['user_id'] == 'admin':
        # abort if there is the user is not logged in
        flash('You need to login to save recipe')
        return redirect(url_for('view_recipe', recipe_id=recipe_element['id']))
    if check_save is None:
        db.execute("INSERT INTO save_recipe (username, title, content, category, recipe_id) VALUES (?, ?, ?, ?, ?)", (
            session['user_id'], recipe_element['title'], recipe_element['content'], recipe_element['category'],
            recipe_element['id']))
        db.commit()
    elif check_save is not None:
        flash('This recipe has already been saved!')
    return redirect(url_for('view_recipe', recipe_id=recipe_element['id']))


@app.route('/saved_recipes', methods=['GET'])
def saved_recipes():
    if session['user_id'] is None:
        flash('You need to login to see save recipes')
        return redirect(url_for('HomePage'))
    db = get_db()
    cur = db.execute('SELECT * FROM save_recipe WHERE username = ?', [session['user_id']])
    saved = cur.fetchall()
    return render_template('saved_recipes.html', saved_recipes=saved)


@app.route('/follow_author', methods=['POST'])
def follow_author():
    db = get_db()
    action = request.form['action']
    if action == 'follow':
        user = request.form['author']
        current_user = session['user_id']
        db.execute('INSERT INTO save_author (author, user) VALUES (?,?)', (user, current_user))
        db.commit()
        return redirect(url_for('user_account', author=user))
    elif action == 'unfollow':
        user = request.form['author']
        current_user = session['user_id']
        cur = db.execute('INSERT INTO save_author (author, user) VALUES (?,?)', [user, current_user])
        return redirect(url_for('user_account', author=user))


@app.route('/user_account')
def user_account():
    db = get_db()
    user = request.args.get('author')
    if user is None:
        user = session['user_id']
    if session['user_id'] is None:
        flash('You need to login to see the account')
        return redirect(url_for('HomePage'))
    cur2 = db.execute('SELECT * FROM recipes WHERE user_id=?', [user])
    created_recipes = cur2.fetchall()
    author_followed = db.execute('SELECT * FROM save_author WHERE user = ?', [session['user_id']])
    author_followed = author_followed.fetchall()
    user_info = db.execute('SELECT * FROM user WHERE username = ?', [user])
    user_info = user_info.fetchone()
    if user != session['user_id']:
        follow_author = db.execute('SELECT * FROM save_author WHERE user = ? and author = ?',
                                   [session['user_id'], user])
        follow_author = follow_author.fetchone()
        author_followed = db.execute('SELECT * FROM save_author WHERE user = ?', [user])
        author_followed = author_followed.fetchall()
        return render_template('user_account.html', user=user, created_recipes=created_recipes,
                               follow_author=follow_author, author_followed=author_followed, user_info=user_info)
    return render_template('user_account.html', user=user, created_recipes=created_recipes,
                           author_followed=author_followed, user_info=user_info)


@app.route('/notifications', methods=['GET'])
def notifications():
    db = get_db()
    cur = db.execute('SELECT * FROM notifications WHERE to_user=?', [session['user_id']])
    my_notifications = cur.fetchall()
    return render_template('notifications.html', my_notifications=my_notifications)


@app.route('/delete_recipe', methods=['POST'])
def delete_recipe():
    """Deletes recipe only if the user is the one that posted the recipe."""
    # If user does not have an account then it will redirect to HomePage and flashes message
    if not session['user_id']:
        flash("Unable to Delete Post!")
        return redirect(url_for('HomePage'))
    else:
        # Deletes the recipe using id to delete.
        db = get_db()
        db.execute('DELETE FROM recipes WHERE id = ?', request.form["id"])
        db.commit()
        db.execute('DELETE FROM save_recipe WHERE recipe_id = ?', request.form['id'])
        db.commit()
        flash("Recipe was successfully deleted!")
    return redirect(url_for('HomePage'))


@app.route('/edit', methods=['GET'])
def edit():
    """Redirects to edit screen"""
    # Checks if user has an account to have access to edit this post.
    if not session['user_id']:
        flash("Unable to Edit Post!")
        return redirect(url_for('HomePage'))
    else:
        # Can edit recipe by id
        args = request.args
        edit_id = args.get('id')
        db = get_db()
        cur = db.execute('SELECT * FROM recipes WHERE id=?', [edit_id])
        recipe = cur.fetchone()
        return render_template('edit.html', recipe=recipe)


@app.route('/edit_recipe', methods=['POST'])
def edit_recipe():
    """Allows changes to be made to recipe using ID"""
    edit_id = request.form['id']
    db = get_db()
    db.execute('UPDATE recipes SET title = ?, category = ?, content = ? WHERE id = ?',
               [request.form['title'], request.form['category'], request.form['content'], request.form['id']])
    db.commit()
    flash('Recipe Was Successfully Updated!')
    return redirect(url_for('view_recipe', recipe_id=edit_id))
