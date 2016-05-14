"""

"""
# from werkzeug.security import generate_password_hash, check_password_hash
# from flask_login import UserMixin
#
# from . import db, login_manager
#
#
# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))
#
#
# class User(db.Model, UserMixin):
#     """
#     Our User model. Users have biographical information, a user id, user name,
#     and password.
#     """
#     __tablename__ = 'users'
#     __bind_key__ = 'users'
#     # columns with no special methods
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(20), unique=True)
#     name = db.Column(db.String(255), index=True)
#     affiliation = db.Column(db.String(64), index=True)
#     state = db.Column(db.String(2), index=True)
#     city = db.Column(db.String(20), index=True)
#
#
#     # password/password_hash
#     password_hash = db.Column(db.String(128))
#
#     @property
#     def password(self):
#         raise AttributeError('password is not a readable attribute')
#
#     @password.setter
#     def password(self, password):
#         self.password_hash = generate_password_hash(password)
#
#     def verify_password(self, password):
#         return check_password_hash(self.password_hash, password)
#
#     # single user/many resources relationship;
#     # use like Resource(..., user=current_user)
#     # then will have list of all of a user's contributions via u.resources
#     resources = db.relationship('Resource', backref='user')
#
#     def __repr__(self):
#         return '<User %r>' % self.name


import datetime as dt

from flask.ext.security import UserMixin, RoleMixin

from . import db

roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('roles.id')))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    __bind_key__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    name = db.Column(db.String(255))
    affiliation = db.Column(db.String(255))
    state = db.Column(db.String(255))
    city = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(255))
    current_login_ip = db.Column(db.String(255))
    login_count = db.Column(db.Integer)

    def __repr__(self):
        return '<models.User[email=%s]>' % self.email


class Role(RoleMixin, db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))





class Resource(db.Model):
    """
    Model to represent a user-contributed resource. Now we'll need to
    set up relationship between the id in this table and the User
    model id, since this is how we can match users to their
    contributions.
    """
    # TODO figure out how to match this to the id from User
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(200), index=True, unique=True)
    uuid = db.Column(db.String(36), index=True, unique=True)
    description = db.Column(db.Text())
    keywords = db.Column(db.Text())
    url = db.Column(db.Text())

    def __repr__(self):
        print self.uuid
        return "<Resource %s:\n\tuser_id: %s,\n\ttitle: %s,\n\tuuid: %s,\n\tdescription: %s,\n\tkeywords: %s,\n\turl: %s>" % (self.id, self.user_id,
                self.title, self.uuid, self.description,
                self.keywords, self.url)
