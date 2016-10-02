"""A friendly and Pythonic API wrapper."""
import collections
from datetime import datetime

import now.helpers
from now.raw import Client

# Convenience classes


class Deployment:
    """A single deployment to now.sh."""
    def __init__(self, data, parent=None):
        # Handle passing id instead of dict
        if isinstance(data, str):
            data = parent[id]._data

        self._data = data
        self.name = data["name"]
        self.id = self.uid = data["uid"]
        self.url = self.host = data["url"]
        self.created = datetime.fromtimestamp(int(data["created"]) / 1000)

    def delete(self):
        """Remove the deployment"""
        pass

    remove = delete  # Alias

    def __del__(self):
        self.delete()

    def __repr__(self):
        return "<Deployment '{}'>".format(self.name)


class Deployments(collections.Mapping):
    """Represents all deployments.

    Serves as a high-level Pythonic API wrapper."""
    def __init__(self):
        self._client = Client()

    def _get_deployments(self):
        deploys = self._client.get_deployments()
        return list(map(Deployment, deploys))

    def __getitem__(self, id):
        deploys = self._get_deployments()
        return list(filter(lambda x: x.id == id, deploys))[0]

    def __iter__(self):
        return iter([d.id for d in self._get_deployments()])

    def __len__(self):
        return len(self._get_deployments())

    def create(self, body):
        return self[self._client.create_deployment(body)["uid"]]

    def create_from_folder(self, path):
        paths, relpaths = now.helpers.recursive_folder_list(path)
        files = [now.helpers.get_file_contents(path) for path in paths]

        return self.create(dict(zip(relpaths, files)))

    @property
    def dict(self):
        """Get the deployments in the 'raw' form of a static dict for faster
        operations.

        Note that we use a comprehension instead of dict(self) because
        dict(self) would make a network request for each deployment, which is
        far too time consuming. With a comprehenison, the dict building is
        simplified to a single request."""
        return {d.id: d for d in self._get_deployments()}

    def __repr__(self):
        return repr(self.dict)
