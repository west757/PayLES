from flask import Flask
from flask_session import Session
from flask_wtf import CSRFProtect
from app.config import Config

flask_app = Flask(__name__)
flask_app.config.from_object(Config)
Session(flask_app)
csrf = CSRFProtect(flask_app)

@flask_app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:;"
    )
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

import app.routes
import app.errors