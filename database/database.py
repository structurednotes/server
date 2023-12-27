from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Initialize the SQLAlchemy ORM instance
db = SQLAlchemy()


def init_db(app):
    """
    Initialize the database with the given Flask app.
    This will configure the database according to the app's configuration and create
    the database tables if they don't already exist.
    """
    db.init_app(app)
    with app.app_context():
        db.create_all()  # Create tables if they don't exist


def get_engine(uri):
    """
    Create and return a new SQLAlchemy engine for the given URI.
    """
    return create_engine(uri, convert_unicode=True)


def get_session(engine):
    """
    Create and return a new SQLAlchemy scoped session using the given engine.
    """
    session_factory = sessionmaker(bind=engine)
    return scoped_session(session_factory)
