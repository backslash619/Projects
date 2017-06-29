# making form api as for validation and other parameters
from flask_wtf import Form
from models import User
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import (DataRequired, Regexp,
                                ValidationError, Length, EqualTo, Email)


# this takes two arguements as form we are currently on can be any form
# and the field we used the method
def name_exists(form, field):
    if User.select().where(User.username == field.data).exists():
        # so this will return boolean and if return true then
        raise ValidationError('Username already exists.')


def email_exists(form, field):
    if User.select().where(User.email == field.data).exists():
        # so this will return boolean and if return true then
        raise ValidationError('Email already exists.')


class RegistrationForm(Form):
    # this is a class which inherits from Form class
    username = StringField(
        # 'Username' its just a placeholder/label
        # validators are used to validate something like data must be required in the field :- we use Datarequired
        # the username should be of specific pattern for that we use regexp
        'Username',
        validators=[
            DataRequired(),
            Regexp(
                r'^[a-zA-Z0-9_]+$',
                message="Username should be letters, numbers and '_' only  "
            ),
            name_exists
        ])
    # we're using the name_exists function as to check if the username exists in the database or not

    # email
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(),
            email_exists
        ])
    # password
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=5),
            EqualTo('password2', message='Password must match.')
        ])
    # we use Length for the minimum length of the password we want
    # EqaulTo is used as to match to something
    password2 = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired()
        ])
    # we can add more validation fields or can build the new form seperately


class LoginForm(Form):
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email()
        ])
    password = PasswordField(
        'Password',
        validators=[
            DataRequired()
        ])


# this is the post form and this is being used in the app.py as view and route it in way
class PostForm(Form):
    content = TextAreaField(
        "What's up ?",
        validators=[
            DataRequired()
        ])
