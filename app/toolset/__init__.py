from flask import Blueprint

toolset = Blueprint('toolset', __name__)

from . import views
