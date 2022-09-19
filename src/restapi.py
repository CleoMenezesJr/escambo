import requests
import json


class ResolveRequests:
    def __init__(self, url, session, payload=None):
        self.url = url
        self.payload = payload
        self.session = session

        # TODO
        # If header is None, guess header content_type
        head = requests.head(self.url)
        if "Content-Type" in head.headers:
            type = head.headers["Content-Type"]
            self.headers = {"Content-Type": type}

    def resolve_get(self):
        response = requests.get(self.url).json()
        try:
            return json.dumps(response, indent=4)
        except requests.exceptions.JSONDecodeError:
            return response.text

    def resolve_post(self):
        data = json.loads(self.payload)
        response = self.session.post(self.url, json=data, headers=self.headers)
        try:
            return json.dumps(response.json(), indent=4)
        except requests.exceptions.JSONDecodeError:
            return response.text
