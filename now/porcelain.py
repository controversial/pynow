"""A friendly and Pythonic API wrapper.

The classes representing mutable data (just 'Deployments') retrieve information
in realtime. When now.deployments[id] is accessed, a network request is made to
return the most up-to-date information. This isn't necessary for other classes,
however, since deployments are immutable.
"""

import collections
from datetime import datetime
import os

import now.helpers
from now.raw import Client

# Convenience classes


class File():
    def __init__(self, data, deployment, client=None):
        self._client = client or Client()

        self._data = data
        self.deployment = deployment

        self.name = self.path = data["name"]
        self.uid = self.id = data["uid"]
        self.type = data["type"]

        self.content = self._client.get_file(self.deployment.id, self.id)


class Files(collections.Mapping):
    """A mapping for files within a deployment.

    Individual deployments are immutable, so this class does not need to be
    'live' like 'Deployments' is."""
    def __init__(self, deployment, client=None):
        self.deployment = deployment
        self._client = client or Client()

        self._data = self._client.get_files(deployment.id)

    def __getitem__(self, uid_or_filename):
        """Access files by UID or by filename."""
        files_matching_uid = list(filter(
            lambda x: x["uid"] == uid_or_filename,
            self._data
        ))
        files_matching_filename = list(filter(
            lambda x: x["name"] == uid_or_filename,
            self._data
        ))
        if files_matching_uid:
            file = files_matching_uid[0]
        elif files_matching_filename:
            file = files_matching_filename[0]
        else:
            raise ValueError(
                "{} did not match the filename or UID of any files".format(
                    uid_or_filename
                )
            )
        return File(file, self.deployment)

    def __iter__(self):
        return iter(map(lambda x: x["uid"], self._data))

    def __len__(self):
        return len(self._data())


class Deployment:
    """A single deployment to now.sh."""
    def __init__(self, data, client=None, parent=None):
        # Handle passing id instead of dict
        if isinstance(data, str):
            data = parent[id]._data

        self._client = client or Client()

        self._data = data
        self.name = data["name"]
        self.id = self.uid = data["uid"]
        self.url = self.host = data["url"]
        self.created = datetime.fromtimestamp(int(data["created"]) / 1000)
        
        self.files = Files(self)

    def delete(self):
        """Remove the deployment"""
        self._client.delete_deployment(self.id)

    remove = delete  # Alias

    def __repr__(self):
        return "<Deployment '{}'>".format(self.name)


class Deployments(collections.Mapping):
    """Represents all deployments.

    Serves as a high-level Pythonic API wrapper."""
    def __init__(self, client=None):
        self._client = client or Client()

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

    def create(self, body, name=None):
        return self[self._client.create_deployment(body, name)["uid"]]

    def create_from_folder(self, path):
        paths, relpaths = now.helpers.recursive_folder_list(path)
        files = [now.helpers.get_file_contents(path) for path in paths]

        return self.create(
            dict(zip(relpaths, files)),
            os.path.split(path)[1]
        )

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