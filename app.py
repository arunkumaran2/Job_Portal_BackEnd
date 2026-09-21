"""Flask application entry point for the Job Portal backend."""

from flask import Flask

from admins_controller.admin_controller import admin_bp
from jobseeker_controller.job_seeker_controller import jobseeker_bp
from recruiters_controller.recruiter_controller import recruiter_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(jobseeker_bp)
    app.register_blueprint(recruiter_bp)
    app.register_blueprint(admin_bp)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
