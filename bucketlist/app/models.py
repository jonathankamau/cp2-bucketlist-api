# This is where you define the models of your application.

# datetime.fromtimestamp(time.time())

import jwt

from datetime import date, datetime
from flask_bcrypt import Bcrypt
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask_sqlalchemy import Model, SQLAlchemy
# from itsdangerous import (TimedJSONWebSignatureSerializer
#                           as Serializer, BadSignature, SignatureExpired)

from sqlalchemy import DateTime, Column


class TimestampedModel(Model):
    created_on = Column(DateTime,
                        nullable=False,
                        default=datetime.now().isoformat(
                            sep=' ',
                            timespec='minutes'))


db = SQLAlchemy(model_class=TimestampedModel)

# db = SQLAlchemy()
auth = HTTPBasicAuth()
bcrypt = Bcrypt()

# roles_users = db.Table(
#     'roles_user',
#     db.Column('user_id', db.Integer(), db.ForeignKey('User.user_id')),
#     db.Column('role_id', db.Integer(), db.ForeignKey('Role.role_id'))
# )


# class Role(db.Model):

#     __tablename__ = 'Role'

#     role_id = db.Column(db.Integer(), primary_key=True)
#     role_name = db.Column(db.String(20), unique=True)
#     description = db.Column(db.String(50))

#     def __init__(self, role_name):
#         self.role_name = role_name

#     def __repr__(self):
#         return '<Role %r>' % (self.role_name)


class User(db.Model):

    __tablename__ = 'User'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    authenticated = db.Column(db.Boolean, nullable=False, default=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    # created_on = db.Column(db.DateTime,
    #                        default=datetime.now().isoformat(
    #                            sep=' ',
    #                            timespec='minutes')
    #                        )

    #    default=datetime.today().strftime(format)

    bucketlist = db.relationship(
        'Bucketlist', backref=db.backref('user', uselist=False),
        lazy='immediate', order_by='Bucketlist.list_id')

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password.encode('utf8'), 12).decode('utf8')
        self.authenticated = False
        self.active = False

    def __repr__(self):
        return '<User %r>' % (self.username)

    def get_id(self):
        """Return username to satisfy Flask-Login's requirements"""
        return self.username

    def is_authenticated(self):
        """Return True if the user is authenticated"""
        return self.authenticated

    def is_active(self):
        """Return if user has activated their account"""
        return self.active

    def is_anonymous(self):
        """False, as anonymous users aren't supported"""
        return False

    @auth.verify_password
    def verify_password(self, password):
        if bcrypt.check_password_hash(self.password, password):
            return True

        return False


class Bucketlist(db.Model):

    __tablename__ = 'Bucketlist'

    list_id = db.Column(db.Integer, primary_key=True)
    list_name = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(100), nullable=True)
    is_completed = db.Column(db.Boolean(), nullable=False, default=False)
    # created_on = db.Column(db.DateTime,
    #                        default=datetime.now().isoformat(
    #                            sep=' ',
    #                            timespec='minutes')
    #                        )
    date_modified = db.Column(db.DateTime,
                              default=datetime.now().isoformat(
                                  sep=' ',
                                  timespec='minutes'))
    # created_by = db.Column(db.Integer, db.ForeignKey(
    #     'User.user_id', ondelete='CASCADE'))

    created_by = db.Column(db.Integer, db.ForeignKey(
        'User.user_id'), nullable=False)

    items = db.relationship(
        'Bucketlist_Item', backref=db.backref('bucketlist', uselist=False),
        lazy='immediate', order_by='Bucketlist_Item.item_id')
    # items = db.relationship('Bucketlist_Item', backref=db.backref(
    #     'item', cascade='delete-orphan', uselist=False, single_parent=True),
    #     lazy='joined',
    #     primaryjoin='Bucketlist_Item.list_id==Bucketlist.list_id')

    def __init__(self, list_name, description, created_by):
        self.list_name = list_name
        self.description = description
        self.created_by = created_by
        self.is_completed = False
        self.date_modified = datetime.now().isoformat(
            sep=' ',
            timespec='minutes')

    def __repr__(self):
        """Return Bucketlist name"""
        return '<Bucketlist %r>' % (self.list_name)

    def get_id(self):
        """Return Bucketlist id"""
        return self.list_id

    def list_is_completed(self):
        """Return True if the all bucketlist items have been completed"""
        return self.is_completed


class Bucketlist_Item(db.Model):

    __tablename__ = 'Bucketlist_Item'

    item_id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey(
        'Bucketlist.list_id'), nullable=False)
    item_name = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(100), nullable=True)
    is_completed = db.Column(db.Boolean(), nullable=False, default=False)
    # created_on = db.Column(db.DateTime, nullable=False,
    #                        default=datetime.now().isoformat(
    #                            sep=' ',
    #                            timespec='minutes'))
    date_modified = db.Column(db.DateTime,
                              default=datetime.now().isoformat(
                                  sep=' ',
                                  timespec='minutes'))

    # items = db.relationship('Bucketlist', backref=db.backref(
    #     'bucketlist',
    #     # cascade='delete-orphan',
    #     uselist=False,
    #     single_parent=True
    # ),
    #     lazy='joined',
    #     # primaryjoin='Bucketlist.list_id'=='Bucketlist_Item.list_id'
    # )

    def __init__(self, item_name, description, list_id):
        self.item_name = item_name
        self.list_id = list_id
        self.description = description
        self.is_completed = False
        self.date_modified = datetime.now().isoformat(
            sep=' ',
            timespec='minutes')

    def __repr__(self):
        """Return Bucketlist item name"""
        return '<Bucketlist %r>' % (self.list_name)

    def get_id(self):
        """Return Bucketlist item id"""
        return self.item_id

    def list_is_completed(self):
        """Return True if item has been completed"""
        return self.is_completed