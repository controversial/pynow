#!python3
import json
import os

import requests

import now.helpers
from now.classes import Deployment


API_ENDPOINT = "https://api.zeit.co/now"
API_TOKEN = os.environ.get("ZEIT_API_TOKEN")
if not API_TOKEN:
    API_TOKEN = input("Zeit API token: ")
    os.environ["ZEIT_API_TOKEN"] = API_TOKEN


class Now:
    """Interface to the now.sh API."""
    def __init__(self, token=API_TOKEN):
        self.token = token

    def _send_request(self, path, body=None, method="GET"):
        req = requests.request(
            method,
            os.path.join(API_ENDPOINT, path),
            json=body,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer " + API_TOKEN
            },
        )
        req.raise_for_status()
        return req.json()

    @property
    def deployments(self):
        """List all deployments."""
        deploys = self._send_request("deployments")["deployments"]
        return list(map(Deployment, deploys))

    def get_deployment(self, id):
        """Get a Deployment object for a deployment with a given id."""
        # Listing all deployments yields more detailed information, so we
        # favor filtering the full list over the /deployments/<id> endpoint
        deploys = self.deployments
        return list(filter(lambda x: x.id == id, deploys))[0]

    def create_deployment(self, body):
        """Create a new deployment.
        
        body should be a dict mapping paths to file contents. For example:
            {
                "app/main.py": "print('Hello!')",
                "app2/main.py": "print('Hi')"
            }
        """
        if "package.json" in body:
            body["package"] = body.pop("package.json")

        # Allow static deployments by inserting a dummy package.json
        if "Dockerfile" not in body and "package" not in body:
            body["package"] = {
                "name": "pythonista-deployment",
                "dependencies": {
                    "list": "latest"
                },
                "scripts": {
                    "start": "list ."
                }
            }

        return Deployment(self._send_request("deployments", body, "POST"))

    def upload_folder(self, path):
        """Upload a folder to now.sh and return the URL."""

        paths, relpaths = now.helpers.recursive_folder_list(path)
        files = [now.helpers.get_file_contents(path) for path in paths]

        body = dict(zip(relpaths, files))

        return self.create_deployment(body)