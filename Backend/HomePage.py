from flask import Blueprint, render_template

HomePage = Blueprint('HomePage', __name__,template_folder='templates')


@HomePage.route('/')
def call_homepage():
    name = None
    return render_template('HomePage.html')