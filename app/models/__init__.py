from flask import Blueprint

modeling = Blueprint('modeling', __name__)

from . import views
