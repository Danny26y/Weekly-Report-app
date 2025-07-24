from flask import Flask
from config import Config
from routes import init_routes


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)


    app.secret_key = 'your-secret-key-here'  # Replace with a real secret key


    init_routes(app)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
