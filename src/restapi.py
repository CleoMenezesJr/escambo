import requests
import json


class ResolveRequests:
    def __init__(self, url, session, payload=None):
        self.url = url
        self.session = session
        if not payload:
            self.payload = payload
        else:
            self.payload = json.loads(payload)

        # TODO
        # If header is None, guess header content_type
        head = requests.head(self.url)
        if "Content-Type" in head.headers:
            type = head.headers["Content-Type"]
            self.headers = {"Content-Type": type}
        else:
            self.headers = None

    def resolve_get(self):
        response = self.session.get(
            self.url,
            json=self.payload,
            headers=self.headers
        )
        try:
            return json.dumps(response.json(), indent=4)
        except requests.exceptions.JSONDecodeError:
            return response.text

    def resolve_post(self):
        response = self.session.post(
            self.url,
            json=self.payload,
            headers=self.headers
        )
        try:
            return json.dumps(response.json(), indent=4)
        except requests.exceptions.JSONDecodeError:
            return response.text
