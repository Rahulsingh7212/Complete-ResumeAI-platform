# loadtest/locustfile.py

import json
import random
import time
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner, WorkerRunner

# ─────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────

# Pre-created test users for load testing
TEST_USERS = [
    {"email": "loadtest1@test.com", "password": "loadtest123"},
    {"email": "loadtest2@test.com", "password": "loadtest123"},
    {"email": "loadtest3@test.com", "password": "loadtest123"},
    {"email": "loadtest4@test.com", "password": "loadtest123"},
    {"email": "loadtest5@test.com", "password": "loadtest123"},
]

# Sample resume text for analysis (short version)
SAMPLE_RESUME_TEXT = """
JOHN DOE
Senior Software Engineer

EXPERIENCE
Senior Software Engineer - Tech Corp (2020-2024)
- Led team of 5 engineers building microservices
- Improved API performance by 40%
- Deployed 50+ features to production

Software Engineer - StartupXYZ (2018-2020)
- Built React frontend serving 100K users
- Implemented CI/CD pipelines
- Reduced bug rate by 30%

EDUCATION
B.S. Computer Science - State University (2018)

SKILLS
Python, JavaScript, React, Node.js, PostgreSQL, Docker, AWS, Git, REST APIs, Agile
"""

SAMPLE_JD = """
Senior Full-Stack Engineer

Requirements:
- 5+ years experience in Python and JavaScript
- Experience with React and Next.js
- Knowledge of PostgreSQL and MongoDB
- AWS or GCP experience
- Docker and Kubernetes
- Strong communication skills
- Experience with CI/CD pipelines
- TypeScript proficiency
"""


class ResumeAIUser(HttpUser):
    """
    Simulates a user of the ResumeAI platform.
    Tests the full user journey: login → upload → analyze → view results.
    """
    wait_time = between(1, 3)

    def on_start(self):
        """Called when a simulated user starts. Login and get token."""
        # Pick a random test user
        user = random.choice(TEST_USERS)
        self.user_email = user["email"]

        # Login
        response = self.client.post(
            "/auth/login",
            json=user,
            name="/auth/login",
        )

        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
            self.authenticated = True
        else:
            self.token = None
            self.headers = {}
            self.authenticated = False

    @task(5)
    def view_dashboard(self):
        """Most common action: view dashboard (GET /auth/me)."""
        if not self.authenticated:
            return

        self.client.get(
            "/auth/me",
            headers=self.headers,
            name="/auth/me",
        )

    @task(3)
    def get_usage(self):
        """Check usage info."""
        if not self.authenticated:
            return

        self.client.get(
            "/analysis/usage",
            headers=self.headers,
            name="/analysis/usage",
        )

    @task(3)
    def get_plan(self):
        """Check plan info."""
        if not self.authenticated:
            return

        self.client.get(
            "/plan/",
            headers=self.headers,
            name="/plan/",
        )

    @task(2)
    def list_resumes(self):
        """List uploaded resumes."""
        if not self.authenticated:
            return

        self.client.get(
            "/resumes/?page=1&limit=10",
            headers=self.headers,
            name="/resumes/",
        )

    @task(2)
    def view_history(self):
        """View analysis history."""
        if not self.authenticated:
            return

        self.client.get(
            "/analysis/history?page=1&limit=10",
            headers=self.headers,
            name="/analysis/history",
        )

    @task(1)
    def get_trends(self):
        """Get score trends."""
        if not self.authenticated:
            return

        self.client.get(
            "/analysis/trends",
            headers=self.headers,
            name="/analysis/trends",
        )

    @task(1)
    def health_check(self):
        """Health check endpoint — no auth needed."""
        self.client.get("/health", name="/health")


class ResumeAIUnauthenticatedUser(HttpUser):
    """
    Simulates unauthenticated traffic hitting public endpoints.
    Tests that the server handles mixed traffic well.
    """
    wait_time = between(0.5, 2)

    @task(3)
    def health_check(self):
        self.client.get("/health", name="/health [public]")

    @task(2)
    def root_endpoint(self):
        self.client.get("/", name="/ [public]")

    @task(1)
    def invalid_login(self):
        self.client.post(
            "/auth/login",
            json={"email": "nonexistent@test.com", "password": "wrong"},
            name="/auth/login [invalid]",
        )

    @task(1)
    def unauthorized_access(self):
        self.client.get(
            "/auth/me",
            name="/auth/me [unauthorized]",
        )