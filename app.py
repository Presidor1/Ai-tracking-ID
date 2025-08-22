from flask import Flask
from config import Config
from routes import routes

# Initialize Flask
app = Flask(__name__)

# Load configuration
app.config.from_object(Config)

# Register blueprints (routes)
app.register_blueprint(routes)

# Root endpoint
@app.route("/")
def index():
    return "✅ Kidnap/Banditry Geolocation AI is running!"

# Entry point
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
