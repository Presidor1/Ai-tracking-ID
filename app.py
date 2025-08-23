import os
from flask import Flask
from config import Config
from routes import routes
from models import db, User
from flask_migrate import Migrate
from flask_login import LoginManager

# =========================
# Initialize Flask
# =========================
app = Flask(__name__, static_folder="static", template_folder="templates")

# Load configuration
app.config.from_object(Config)

# Ensure uploads/results folders exist
os.makedirs(os.path.join("static", "uploads"), exist_ok=True)
os.makedirs(os.path.join("static", "results"), exist_ok=True)

# =========================
# Database + Migrations
# =========================
db.init_app(app)
migrate = Migrate(app, db)

# =========================
# Flask-Login Manager
# =========================
login_manager = LoginManager()
login_manager.login_view = "routes.login"  # redirect to login page if unauthorized
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    """Flask-Login user loader"""
    return User.query.get(int(user_id))

# =========================
# Register Blueprints
# =========================
app.register_blueprint(routes)

# =========================
# Root endpoint
# =========================
@app.route("/")
def index():
    return "✅ Kidnap/Banditry Geolocation AI is running with DB + Auth + Migrations!"

# =========================
# Entry point
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
