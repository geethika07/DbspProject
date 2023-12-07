import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))

# Load environment variables
load_dotenv()


class Config(object):
    # General config
    SECRET_KEY = os.getenv("SECRET_KEY", "DatabaseSystemPrinciples")
    FLASK_APP = os.getenv("FLASK_APP", "app.py")
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "development")


class ProductionConfig(Config):
    FLASK_DEBUG = "production"
