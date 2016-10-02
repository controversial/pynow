from datetime import datetime


class Deployment:
    """A single deployment to now.sh."""
    def __init__(self, data):
        self.name = data["name"]
        self.id = self.uid = data["uid"]
        self.url = data["url"]
        self.created = datetime.fromtimestamp(int(data["created"]) / 1000)
