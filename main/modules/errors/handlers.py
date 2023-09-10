from flask import Blueprint, render_template

errors = Blueprint('errors', __name__)


@errors.app_errorhandler(404)
def error_404(error):
    help_text = "Whatever you're looking couldn't be found. Was it deleted? Did it ever exit?"
    return render_template('errors/generic-error.html',
                           help_text=help_text,
                           status=404,
                           error=error), 404


@errors.app_errorhandler(403)
def error_403(error):
    help_text = "If you're reading this, then you were " \
                "probably trying to do something you're not supposed to. 👀"
    return render_template('errors/generic-error.html',
                           help_text=help_text,
                           error=error,
                           status=403), 403


@errors.app_errorhandler(401)
def error_401(error):
    help_text = "The server doesn't recognize you. Try logging in again."
    return render_template('errors/generic-error.html',
                           help_text=help_text,
                           error=error,
                           status=401), 401


@errors.app_errorhandler(500)
def error_401(error):
    help_text = "Wow something really fucked up. You'll have to check the server logs."
    return render_template('errors/generic-error.html',
                           help_text=help_text,
                           error=error,
                           status=500), 500
