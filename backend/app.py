from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from database import init_db, create_admin_user, check_db_connection, get_db_stats, db
from database import User, ParkingLot, ParkingSpot, Reservation
from extensions import redis_client, REDIS_AVAILABLE
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.user import user_bp
from tasks.celery_app import make_celery
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize database FIRST (before other extensions)
    init_db(app)
    
    # Initialize other extensions
    jwt = JWTManager(app)

    # Helpful JSON responses for JWT errors to aid debugging
    @jwt.unauthorized_loader
    def missing_loader(err_msg):
        # No JWT present in request
        print(f"JWT unauthorized: {err_msg}")
        return jsonify({'message': 'Missing Authorization Header'}), 401

    @jwt.invalid_token_loader
    def invalid_token_loader(err_msg):
        print(f"JWT invalid token: {err_msg}")
        return jsonify({'message': f'Invalid token: {err_msg}'}), 422

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        print(f"JWT expired for payload: {jwt_payload}")
        return jsonify({'message': 'Token has expired'}), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        print(f"JWT revoked for payload: {jwt_payload}")
        return jsonify({'message': 'Token has been revoked'}), 401

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Initialize Celery
    try:
        celery = make_celery(app)
        app.celery = celery
    except Exception as e:
        print(f"Warning: Celery initialization failed: {str(e)}")
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    
    # Root route - API information
    @app.route('/')
    def index():
        db_status = check_db_connection()
        return jsonify({
            'message': 'VPMS API Server',
            'version': '1.0.0',
            'database': {
                'status': 'connected' if db_status else 'disconnected',
                'path': os.path.join(os.path.dirname(__file__), 'vpms.db')
            },
            'redis': {
                'status': 'available' if REDIS_AVAILABLE else 'unavailable'
            },
            'endpoints': {
                'authentication': {
                    'POST /api/user/register': 'Register new user',
                    'POST /api/user/login': 'User login',
                    'POST /api/admin/login': 'Admin login'
                },
                'admin': {
                    'GET /api/admin/stats': 'Dashboard statistics',
                    'GET /api/admin/parking-lots': 'List parking lots',
                    'POST /api/admin/parking-lots': 'Create parking lot',
                    'GET /api/admin/users': 'List all users'
                },
                'user': {
                    'GET /api/user/stats': 'User dashboard statistics',
                    'GET /api/user/parking-lots/available': 'Get available lots',
                    'POST /api/user/book-parking': 'Book parking spot'
                }
            },
            'default_admin': {
                'username': 'admin',
                'password': 'admin123'
            }
        }), 200
    
    # Health check endpoint
    @app.route('/health')
    def health():
        db_status = check_db_connection()
        stats = get_db_stats() if db_status else {}
        return jsonify({
            'status': 'healthy' if db_status else 'unhealthy',
            'database': 'connected' if db_status else 'disconnected',
            'redis': 'available' if REDIS_AVAILABLE else 'unavailable',
            'stats': stats
        }), 200 if db_status else 503
    
    # Create admin user after database is initialized
    with app.app_context():
        if check_db_connection():
            create_admin_user()
        else:
            print("❌ Database connection failed. Admin user not created.")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)

