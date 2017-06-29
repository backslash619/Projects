import datetime

from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from peewee import *

DATABASE = SqliteDatabase("social.db")


class User(UserMixin, Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    # we use 100 length as we use for hashing
    # and for hashing we use
    # flask-bcrypt
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)

    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)  # orderby accepts tuples and - sign is for the desc order

    def following(self):
        """the user that we are following"""
        return (
            User.select().join(
                Relationship, on=Relationship.to_user
            ).where(
                Relationship.from_user == self
            )
        )
        # select the ones that i am related to as from_user is the current user
        #  as select contains all the attribute as we join the tables
        # we are going to return the from the various  tables so we join the User Post and Relationship
        # and on is the attribute as on  related_name = Relationship  on which tableto get the column

    def followers(self):
        """get users following the curren_user """
        return (
            User.select().join(
                Relationship, on=Relationship.from_user
            ).where(
                Relationship.to_user == self
            )
        )

    def get_posts(self):
        # as we're using this method to get the posts
        # and the self is used to get the current instance user posts [logged in user]
        # these get the posts belongs to a certain user
        return Post.select().where(Post.user == self)

    def get_stream(self):
        # this is just same as get_posts as the people we follow
        return Post.select().where(
            (Post.user << self.following()) or
            (Post.user == self)
        )

    # it's going to be difficult that in order to create  a User Instance to call the create_user() method if it's a
    # normal method then we can access the method by just instance like instance.create_user as we use self as the
    # parameter to access it by using instance but here with classmethod and cls as parameter so  what cls does it
    # just create the User(Model) instance whenever this method called cls used as where we refer to the class method
    #  it belogns to it's like User.create which creates the instance
    @classmethod
    # whenever we want to create the new user we use the create_user() method
    def create_user(cls, username, password, email, admin=False):
        try:
            with DATABASE.transaction():
                cls.create(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),  # never save the password in palin text
                    is_admin=admin
                )
        except IntegrityError:
            raise ValueError("User Already Exists!!")


# saving the posts in db
class Post(Model):
    timestamp = DateTimeField(default=datetime.datetime.now)  # taging the time the user posted
    user = ForeignKeyField(
        rel_model=User,  # this is the rel model as this user pints out to User model above
        related_name='posts'  # this is from peewee this is the realted name of the model which points out to the User
        # model or can be anythin  rel_model equals to
    )

    class Meta:
        databse = DATABASE
        order_by = ('-timestamp',)  # we tuple as the order_by clause instead of lsit asitca't be changed or
        # we can give another param to sort by that attribute


class Relationship(Model):
    from_user = ForeignKeyField(
        User, related_name='relationships'
    )
    to_user = ForeignKeyField(
        User, related_name='related_to'
    )

    class Meta:
        database = DATABASE
        # tells the database how to rwmwmber the tuple
        indexes = (
            (('from_user', 'to_user'), True)
        )


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Post, Relationship], safe=True)
    DATABASE.close()
