from datetime import datetime
import now


class Deployment:
    """A class representing single deployment to now.sh."""
    def __init__(self, data):
        if not all([key in data for key in ["name", "url", "created"]]):
            data = now.Now().get_deployment(data["uid"])._data

        self._data = data
        self.name = data["name"]
        self.id = self.uid = data["uid"]
        self.url = self.host = data["url"]
        self.created = datetime.fromtimestamp(int(data["created"]) / 1000)

    def __repr__(self):
        return "<Deployment '{}' from {}>".format(
            self.name,
            self.created.strftime("%b %d")
        )
