from flask import Flask
import os
from database import init_app

def create_app():
    app = Flask(__name__)
    
    app.config['DATABASE'] = os.path.join(app.instance_path, 'supermarket.db')
    app.config['SECRET_KEY'] = 'dev-key-change-in-production'
    
    os.makedirs(app.instance_path, exist_ok=True)
    
    init_app(app)

    from routes import products, inventory, sales, procurement, dashboard
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(procurement.bp)
    app.register_blueprint(sales.bp)
    app.register_blueprint(products.bp)
    app.register_blueprint(inventory.bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)