from flask import Flask
from app.database import init_db

def create_app():
    app = Flask(__name__)

    init_db(app)

    #User Routes
    from app.routes.users import user_controller
    user_controller(app)

    from app.routes.products import product_controller
    product_controller(app)

    return app
