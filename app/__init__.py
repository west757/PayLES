from flask import Flask
from flask_session import Session
from flask_wtf import CSRFProtect
from app.config import Config

flask_app = Flask(__name__)
flask_app.config.from_object(Config)
Session(flask_app)
csrf = CSRFProtect(flask_app)

import app.routes
import app.errors