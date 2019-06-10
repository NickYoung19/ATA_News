from flask import Blueprint
# create blueprint and set the prefix
passport_blu = Blueprint("passport", __name__, url_prefix='/passport')

from . import views
