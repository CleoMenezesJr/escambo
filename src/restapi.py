import requests
import json


class ResolveRequests:

    def __init__(self, url):
        self.url = url

    def resolve_get(self):
        data = requests.get(self.url).json()
        format_data = json.dumps(data, indent=4)
        return format_data
