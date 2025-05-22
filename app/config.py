import os

from flask.cli import load_dotenv


# Dynamically expose all env keys
class Config:
    def __init__(self, env_file=".env"):
        load_dotenv(path=env_file)
        for key, value in os.environ.items():
            setattr(self, key.upper(), value)
