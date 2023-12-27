import os
import logging


class Config:
    ENV = os.getenv("FLASK_ENV", "development")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    if ENV == "production":
        SQLALCHEMY_DATABASE_URI = "postgresql://username:password@localhost/dbname"
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///api_calls_dev.db"


def setup_logging():
    """Configure the application's logging setup."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - [%(name)s] %(message)s",
        handlers=[logging.StreamHandler()],
    )
