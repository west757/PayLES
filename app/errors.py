from flask import render_template, make_response, jsonify
from werkzeug.exceptions import RequestEntityTooLarge
from app import flask_app

@flask_app.errorhandler(413)
def too_large(e):
    return make_response(jsonify(message="File is too large"), 413)

@flask_app.errorhandler(RequestEntityTooLarge)
def file_too_large(e):
    return 'File is too large', 413

@flask_app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404