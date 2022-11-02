import os
from flask import Flask, session, g, render_template, redirect, flash, jsonify, request
from models import db, connect_db, User, Record
from forms import SignupForm, LoginForm
from sqlalchemy.exc import IntegrityError
from math_exercise import create_math_problem
from datetime import datetime
from sqlalchemy import desc

app = Flask(__name__)
from flask_debugtoolbar import DebugToolbarExtension

CURR_USER_KEY = 'curr_user'

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///bei'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
#toolbar = DebugToolbarExtension(app)

connect_db(app)

##############################################################################
# User signup/login/logout helper functions
@app.before_request
def add_user_to_g():
    """If a user is logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

def user_authorized():
    """Check if user is in Flask global object."""

    if g.user:
        return True
    else:
        return False

##########################################
# Other helper functions
def get_stats():
    """Function to get user stats.
       Returns number of times played, highest math score, and highest trivia score. """

    # Time played
    all_records = Record.query.filter_by(user=g.user).all()
    times_played = len(all_records)

    # Max math score
    high_score_math = [r.math_score for r in all_records if r.math_score != 'Not completed']
    try: high_score_math = max(high_score_math)
    except: high_score_math = 0

    # Max Trivia score
    high_score_trivia = [r.trivia_score for r in all_records if r.trivia_score != 'Not completed']
    try: high_score_trivia = max(high_score_trivia)
    except: high_score_trivia = 0
    return times_played, high_score_math, high_score_trivia

##############################################################################
# User login routes
@app.route('/signup', methods=["GET", "POST"])
def handle_signup():
    """Show and process signup form."""
    if user_authorized():
        return redirect('/')
    form = SignupForm()
    if form.validate_on_submit():
        try:
            new_user = User.signup(username=form.username.data,
                        password = form.password.data,
                        email = form.email.data,
                        first_name = form.first_name.data,
                        last_name = form.last_name.data)
            db.session.commit()
            do_login(new_user)
            return redirect('/')
        except IntegrityError:
            flash('Sorry, that username is taken.')
    return render_template('signup.html', form=form)

@app.route('/login', methods=["GET","POST"])
def handle_login():
    """Show and process log in form."""

    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(username = form.username.data,
        password = form.password.data)

        if (user):
            do_login(user)
            return redirect('/')
        else:
            flash('Invalid username or password.')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    """Log user out and redirect to log in."""

    if user_authorized():
        do_logout()
    return redirect('/login')

##############################################################################
# Homepage
@app.route('/')
def show_homepage():
    """Show homepage with info about brain exercises."""
    if g.user:
        # Get first 5 entries of user history for brief homepage summary
        records = Record.query.filter_by(user_id=g.user.id).order_by(desc(Record.id)).limit(5).all()
        return render_template('homepage.html', records=records)
    return render_template('homepage.html')

##############################################################################
# User detail page 
@app.route('/user/<user_id>')
def show_user_details(user_id):
    """Show all user history and noteworthy stats."""
    # Make sure user can only access their own user detail page
    if g.user and g.user.id == int(user_id):
        times_played, high_score_math, high_score_trivia = get_stats()
        records = Record.query.filter_by(user_id=user_id).order_by(desc(Record.id)).all()
        return render_template('user_details.html', times_played=times_played, high_score_math=high_score_math, high_score_trivia=high_score_trivia, records=records)
    return redirect('/')
##############################################################################
# Exercise Routes
@app.route('/trivia')
def show_trivia():
    """Play trivia exercise."""
    return render_template('trivia.html')

@app.route('/trivia/instructions')
def show_trivia_instructions():
    """Show trivia instructions."""
    return render_template('trivia_instructions.html')

@app.route('/math/instructions')
def show_math_instructions():
    """Show math isntructions."""
    return render_template('math_instructions.html')

@app.route('/math')
def show_math():
    """Complete math exercises."""
    return render_template('math.html')

@app.route('/get-math')
def get_math_problem():
    """Generate simple math problem."""
    problem = create_math_problem(10) # CAN CHANGE DIFFICULTY BASED ON USER SETTINGS LATER
    resp = jsonify({'problem': problem})
    return resp

@app.route('/reading/instructions')
def show_reading_instructions():
    """Show reading instructions."""
    return render_template('reading_instructions.html')

@app.route('/reading')
def show_reading():
    """Show reading passage"""
    return render_template('reading.html')

@app.route('/congrats')
def show_congrats():
    """Congratulate user for completing exercises."""
    if g.user:
        # Most recent scores
        curr_trivia_score = session.get('trivia_score')
        curr_math_score = session.get('math_score')
        # Clear them from session
        session['trivia_score'] = None
        session['math_score'] = None

        times_played, high_score_math, high_score_trivia = get_stats()
        return render_template('congrats.html', times_played=times_played, high_score_math=high_score_math, high_score_trivia=high_score_trivia, curr_trivia_score=curr_trivia_score, curr_math_score=curr_math_score)
    return render_template('congrats.html')


##############################################################################
# Save stats routes
@app.route('/save-stats/trivia', methods=["POST"])
def save_trivia_stats():
    """Save trivia stats to Flask session."""
    data = request.get_json()
    new_trivia_score = data.get('trivia_score')
    session['trivia_score'] = new_trivia_score
    return ('', 204)

@app.route('/save-stats/math', methods=["POST"])
def save_math_stats():
    """Save math stats to Flask session."""
    data = request.get_json()
    new_math_score = data.get('math_score')
    session['math_score'] = new_math_score
    return ('', 204)
    
@app.route('/save-stats', methods=["POST"])
def save_stats():
    """Save all stats to database."""
    if g.user:
        new_trivia_score = session.get('trivia_score', "Not completed")
        new_math_score = session.get('math_score', "Not completed")
        date = datetime.now().date()
        date_formatted = date.strftime("%m/%d/%Y")
        new_record = Record(user_id = g.user.id, trivia_score = new_trivia_score, math_score = new_math_score, date = date_formatted)
        db.session.add(new_record)
        db.session.commit()
    return redirect('/congrats')