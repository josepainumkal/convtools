from . import db


class User(db.Model):
    """
    Our User model. Users have biographical information, a user id, user name,
    and password.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    affiliation = db.Column(db.String(64), index=True)
    state = db.Column(db.String(2), index=True)
    city = db.Column(db.String(20))
    email = db.Column(db.String(20), unique=True)
    # user_name = db.Column(db.String(20), unique=True)
    # passwd = db.Column(db.String(20), primary_key=True)

    def __repr__(self):
        return '<User %r>' % self.user_name
