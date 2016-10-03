"""Raw wrapper for all API calls."""

import json
import os

import requests

from now import API_ENDPOINT, API_TOKEN


class Client:
    """Direct interface to the now.sh API."""

    def __init__(self, token=API_TOKEN):
        self.token = token

    def _send_request(self, path, body=None, method="GET", raw=False):
        """Make a request to the API with the appropriate headers."""
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
        if raw:
            return req.content
        else:
            return req.json()

    # API wrapper

    def get_deployments(self):
        """List all deployments."""
        return self._send_request("deployments")["deployments"]

    def get_deployment(self, id):
        """Get full deployment info for a deployment with a given id."""
        return self._send_request("deployments/{}".format(id))

    def create_deployment(self, body, name=None):
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
                "name": name or "pythonista-deployment",
                "dependencies": {
                    "list": "latest"
                },
                "scripts": {
                    "start": "list ."
                }
            }

        return self._send_request("deployments", body, "POST")

    def delete_deployment(self, id):
        return self._send_request("deployments/{}".format(id), method="DELETE")

    def get_files(self, id):
        return self._send_request("deployments/{}/files".format(id))

    def get_file(self, id, fileid):
        return self._send_request(
            "deployments/{}/files/{}".format(id, fileid),
            raw=True
        )
