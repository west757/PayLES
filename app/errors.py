from flask import render_template
from werkzeug.exceptions import RequestEntityTooLarge
from app import flask_app

@flask_app.errorhandler(RequestEntityTooLarge)
def file_too_large(e):
    return render_template('errors.html', code=413, message="File is too large"), 413

@flask_app.errorhandler(400)
def bad_request(e):
    return render_template('errors.html', code=400, message="Bad Request"), 400

@flask_app.errorhandler(401)
def unauthorized(e):
    return render_template('errors.html', code=401, message="Unauthorized"), 401

@flask_app.errorhandler(403)
def forbidden(e):
    return render_template('errors.html', code=403, message="Forbidden"), 403

@flask_app.errorhandler(404)
def page_not_found(e):
    return render_template('errors.html', code=404, message="Page Not Found"), 404

@flask_app.errorhandler(413)
def too_large(e):
    return render_template('errors.html', code=413, message="File is too large"), 413

@flask_app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors.html', code=500, message="Internal Server Error"), 500