import json

import requests


class ResolveRequests:
    def __init__(self, url, session, cookies=None, parameters=None):
        self.url = url
        self.session = session
        self.cookies = cookies
        self.parameters = parameters

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
            json=self.parameters,
            headers=self.headers,
            cookies=self.cookies,
        )

        status_code = response.status_code
        msg_status_code = requests.status_codes._codes[status_code][0]

        return self.formated_response(response, status_code, msg_status_code)

    def resolve_post(self):
        response = self.session.post(
            self.url, json=self.parameters, headers=self.headers
        )

        status_code = response.status_code
        msg_status_code = requests.status_codes._codes[status_code][0]

        return self.formated_response(response, status_code, msg_status_code)

    def formated_response(self, response, status_code, msg_status_code):
        status = f"{status_code} {msg_status_code}".title().replace("_", " ")

        try:
            return [
                json.dumps(response.json(), indent=4),
                status,
            ]
        except requests.exceptions.JSONDecodeError:
            return [response.text, status]
