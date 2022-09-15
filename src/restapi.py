import requests


class ResolveRequests:

    def __init__(self, url):
        self.url = url

    def _resolve_get(self):
        return requests.get(self.url).text
