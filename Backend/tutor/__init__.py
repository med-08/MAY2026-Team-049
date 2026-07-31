from flask import Blueprint

tutor_bp = Blueprint('tutor', __name__, url_prefix='/tutor', template_folder='../templates')

from tutor import routes
