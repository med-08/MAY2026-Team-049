from flask import Blueprint

parent_bp = Blueprint('parent', __name__, url_prefix='/parent', template_folder='../templates')

from parent import routes
