"""Static config variables to use in the app"""

import os

_base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Export the templates directory path


class Config:
    TEMPLATES_DIRECTORY = os.path.join(_base_dir, "templates")
    DATABASE_URL = os.getenv("DATABASE_URL")
    DATABASE_URL_SYNC = os.getenv("DATABASE_URL_SYNC")


config = Config
