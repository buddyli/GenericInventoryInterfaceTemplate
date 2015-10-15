from GenericInventory import db, app
from flask.ext.sqlalchemy import BaseQuery

# The inventory uses Flask-Sqlalchemy.  I think it's a cool way of relating
# database rows to Python objects.  Easy to learn.
# Flask-SQLAlchemy setup
db.Model.metadata.reflect(db.engine)


# Hook up existing tables to flask sqlalchemy
class Sample(db.Model):
    """
    Table for CONTAINER
    """
    __table__ = db.Model.metadata.tables['GENERICINVSAMPLE']


class Container(db.Model):
    """
    Table for Oligo
    """
    __table__ = db.Model.metadata.tables['GENERICINVCONTAINER']


class Aliquot(db.Model):
    """
    Table for OLIGODESIGN
    """
    __table__ = db.Model.metadata.tables['GENERICINVALIQUOT']
