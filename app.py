import os
from flask import Flask, render_template
from config import Config
from routes import routes
from models import db, User
from flask_migrate import Migrate
from flask_login import LoginManager, current_user

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
login_manager.login_view = "routes.login"  # where to redirect unauthorized users
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
# Root + Error Pages
# =========================
@app.route("/")
def index():
    """Landing page redirect to upload form"""
    return render_template("index.html", title="Kidnap/Banditry Geolocation AI", user=current_user)

@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", message="Page not found"), 404

@app.errorhandler(500)
def server_error(error):
    return render_template("error.html", message="Internal server error"), 500

# =========================
# Entry point
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
