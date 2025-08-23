import os
from flask import Flask, redirect, url_for
from config import Config
from routes import routes
from models import db, User
from flask_migrate import Migrate
from flask_login import LoginManager

# =========================
# Initialize Flask App
# =========================
app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)

# Load configuration
app.config.from_object(Config)

# Ensure required folders exist
os.makedirs(os.path.join("static", "uploads"), exist_ok=True)
os.makedirs(os.path.join("static", "results"), exist_ok=True)

# =========================
# Database & Migrations
# =========================
db.init_app(app)
migrate = Migrate(app, db)

# =========================
# Flask-Login Manager
# =========================
login_manager = LoginManager()
login_manager.login_view = "routes.login"  # Redirect to login if user is not authenticated
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    """Flask-Login user loader (fetch user by ID)."""
    try:
        return User.query.get(int(user_id))
    except Exception as e:
        app.logger.error(f"Error loading user: {e}")
        return None

# =========================
# Register Blueprints
# =========================
app.register_blueprint(routes)

# =========================
# Root Endpoint
# =========================
@app.route("/")
def index():
    """Redirect users to the homepage (upload form)."""
    return redirect(url_for("routes.home"))

# =========================
# Error Handlers
# =========================
@app.errorhandler(404)
def not_found(error):
    """Redirect to home if page not found."""
    return redirect(url_for("routes.home"))

@app.errorhandler(500)
def server_error(error):
    """Return a user-friendly message for server errors."""
    return "⚠️ Internal Server Error. Please try again later.", 500

# =========================
# Entry Point for Local Development
# =========================
if __name__ == "__main__":
    # Debug mode is only recommended for development, disable in production
    app.run(host="0.0.0.0", port=5000, debug=True)
