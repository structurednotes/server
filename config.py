import os


class Config:
    ENV = os.getenv("FLASK_ENV", "development")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    if ENV == "production":
        SQLALCHEMY_DATABASE_URI = "postgresql://username:password@localhost/dbname"
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///api_calls_dev.db"
