#!python3
import os

API_ENDPOINT = "https://api.zeit.co/now"
API_TOKEN = os.environ.get("ZEIT_API_TOKEN")
if not API_TOKEN:
    API_TOKEN = input("Zeit API token: ")
    os.environ["ZEIT_API_TOKEN"] = API_TOKEN

from now.porcelain import Deployments
from now.raw import Client as RawClient

deployments = Deployments()

__all__ = ["deployments", "Client", "API_TOKEN"]