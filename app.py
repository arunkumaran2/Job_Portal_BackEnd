"""Flask application entry point for the Job Portal backend."""

from flask import Flask

from jobseeker_controller.job_seeker_controller import jobseeker_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(jobseeker_bp)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
