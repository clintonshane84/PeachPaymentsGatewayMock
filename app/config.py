import base64
import os

from flask.cli import load_dotenv


# Dynamically expose all env keys
class Config:
    def __init__(self, env_file=".env"):
        load_dotenv(dotenv_path=env_file)
        for key, value in os.environ.items():
            setattr(self, key.lower(), value)
