
# this file is saved for future use of adding web_app
import os
from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.getenv("APP_ENV", default="development") # use "production" on a remote server