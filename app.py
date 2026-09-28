import os
from flask import Flask, render_template
from config import Config
from models import db
from routes import main_bp, consultation_bp, chat_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure required directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.root_path, 'instance'), exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    # Register Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(consultation_bp)
    app.register_blueprint(chat_bp)

    # Basic Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', content_override="404 - Page Not Found"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('base.html', content_override="500 - Internal Server Error"), 500

    # Initialize database tables
    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    print("Starting InsaafAI Legal Consultancy Platform Foundation...")
    print("Access application at http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
