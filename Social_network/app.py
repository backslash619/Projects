from flask import (Flask, g, render_template, redirect, url_for, flash)
from flask_bcrypt import check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

import models
from forms import RegistrationForm, LoginForm, PostForm  # importing the forms module to use it in our app

app = Flask(__name__)
app.secret_key = "lkjaoirfef.fsdjfsdofsdfsdfsdfad/asflkjvldffkjdfg"  # we use secret for the sessions

# setting up login manager
login_manager = LoginManager()  # creating an instance of login manager
login_manager.init_app(app)  # passing our app.py as app
login_manager.login_view = 'login'  # this is the login view as specified as


# login method below if we want to change it we can


# this is just redirectin the the user as is user doesn't logged in then redirect to login page

# function is used by login manager as to lookup for the user
@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:  # doesnotexixt comes from peewee
        # this exception is raised if the loaduser doesnot find the userid in the db
        # hence peewee databse returns an error as it doesn't exist
        return None


DEBUG = True
HOST = '0.0.0.0'
PORT = 8080


@app.before_request  # this is just going to be the the method which going to run before each request
#  and if error in the request then stop handling
# further request like connecting to database pr getting to know the currentuser
def before_request():
    """connect to database before each request"""
    # noinspection PyUnresolvedReferences
    g.db = models.DATABASE
    g.db.get_conn()
    # g.db is the used to make the thing  global as
    # the element/function/thing can be used anywhere   
    g.user = current_user
    # before request it's just goinf to find the current_user for us


@app.after_request
# it takes the response as parameter
def after_request(response):
    """close the databse connection after each response"""
    g.db.close()
    return response


@app.route('/register', methods=('GET', 'POST'))
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash("Registered Successfully !!", "Success")  # the second parameter is for the category
        # once the validation process is done then we can extract the info from the form and
        # create a new user
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        # if every thing went well then we render this to the index page
        return redirect(url_for('login'))
    # if every thing does'nt go well then redirect it to same page
    return render_template('Register.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            # no we try to check for the user if it exists in the db or not
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Email or Password doesn't match!!", "error")
        # flash message is kind of ambiguos
        # so if error doesn;t occur then else we get the user
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've logged in!!", "success")
                return redirect(url_for('index'))
            else:
                flash("Email or Password doesn't match!!", "error")
    return render_template('Login.html', form=form)


@app.route('/new_post', methods=('GET', 'POST'))
# this is view route to the post form and then if we want to redirect to
# the stream page or we can use ajax to pop  the textfield.
@login_required  # we don't want any no logged in users to post the posts
def post():
    form = PostForm()
    if form.validate_on_submit():
        models.Post.create(
            user=g.user._get_current_object(),
            content=form.content.data.strip()
        )
        flash("Message posted!!!", "success")
        return redirect(url_for('index'))
    return render_template('Post.html', form=form)


@app.route('/stream')  # show  posts of the current logged in user
@app.route('/stream/<username>')  # show the posts of the user which we want to see as we can see all others post
def stream(username=None):
    template = 'stream.html'  # as we're keeping the deafult view to display the content
    if username and username != current_user.username:
        user = models.User.select().where(models.User.username ** username).get()  # what this query is doing is taking all the users whatever
        #  we'have clicked on or we want to see as get the user which lookesalike for that we use **
        stream = user.posts.limit(100)  # this gets us the post of that users
    else:
        stream = current_user.get_stream().limit(100)  # as this gives the user which has logged in
        user = current_user  # and user got reintialized to current_user
    if username:
        template = 'user_stream.html'
    return render_template(template, stream=stream, user=user )


@app.route('/post/<int:post_id>')
def view_post(post_id):
        posts =  models.Post.select().where(models.Post.id == post_id)# here we are taking the posts which has
        # id as returns a group
        return render_template('stream.html', stream = posts)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been Logged out!! Please visit Again.", "success")
    return redirect(url_for('index'))


@app.route('/')
def index():
    stream = models.Post.select().limit(100)  # this is our  stream of posts
    return render_template("stream.html", stream=stream)  # here we are rendering to stream.html
    # where all the posts is being displayed even if not logged in
    # as passing all the posts in the stream var


# making a route as the user we want to follow
@app.route('/follow/<username>')
# showing the username in url might cause some security issues
@login_required
def follow(username):
    try:
        to_user = models.User.get(
            models.User.username ** username)  # gets the username which looks alike the user in the database
    except models.DoesNotExist:
        pass
    else:  # else we want to create a new relationship
        try:
            models.Relationship.create(
                from_user=g.user._get_current_object(),
                to_user=to_user
            )
        except models.IntegrityError:
            pass
        else:
            flash("You're now following {}!".format(to_user.username), "success")
    return redirect(url_for('stream', username=to_user.username))


@app.route('/unfollow/<username>')  # showing the username in url might cause some security issues
@login_required
def unfollow(username):
    try:
        to_user = models.User.get(
            models.User.username ** username)  # gets the username which looks alike the user in the database
    except models.DoesNotExist:
        pass
    else:  # else we want to create a new relationship
        try:
            models.Relationship.get(
                from_user=g.user._get_current_object(),
                to_user=to_user
            ).delete_instance()# as deleting the relation
        except models.IntegrityError:
            pass
        else:
            flash("You've unfollowed {}!".format(to_user.username), "success")
    return redirect(url_for('stream', username=to_user.username))


if __name__ == "__main__":
    models.initialize()
    try:
        models.User.create_user(  # basically count as SuperUser
            username='user_tarun',
            email='tarunkmr1234@gmail.com',
            password='password',
            admin=True
        )
    except ValueError:
        pass

    app.run(debug=DEBUG, host=HOST, port=PORT)
