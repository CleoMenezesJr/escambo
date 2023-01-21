import json

import requests


class ResolveRequests:
    def __init__(
        self,
        url: str,
        session: requests.sessions.Session,
        cookies: dict = None,
        headers: dict = None,
        body: dict = None,
        parameters: dict = None
    ) -> None:

        self.url = url
        self.session = session
        self.cookies = cookies
        self.headers = cookies
        self.body = body
        self.params = parameters

    def resolve_get(self) -> list:
        response = self.session.get(
            self.url,
            json=self.body,
            headers=self.headers,
            cookies=self.cookies,
            params=self.params
        )

        return self.formated_response(response)

    def resolve_post(self) -> list:
        response = self.session.post(
            self.url,
            json=self.body,
            headers=self.headers,
            cookies=self.cookies,
            params=self.params
        )

        return self.formated_response(response)

    def resolve_put(self) -> list:
        response = self.session.put(
            self.url,
            json=self.body,
            headers=self.headers,
            cookies=self.cookies,
            params=self.params
        )

        return self.formated_response(response)

    def resolve_patch(self) -> list:
        response = self.session.patch(
            self.url,
            json=self.body,
            headers=self.headers,
            cookies=self.cookies,
            params=self.params
        )

        return self.formated_response(response)

    def resolve_delete(self) -> list:
        response = self.session.patch(
            self.url,
            json=self.body,
            headers=self.headers,
            cookies=self.cookies,
            params=self.params
        )

        return self.formated_response(response)

    def formated_response(self, response: requests.models.Response) -> list:
        status_code = response.status_code
        msg_status_code = requests.status_codes._codes[status_code][0]
        status = f"{status_code} {msg_status_code}".title().replace("_", " ")

        if str(response.headers.get("content-type")).startswith(
            "application/json"
        ):
            return [json.dumps(response.json(), indent=4), status, "json"]
        else:
            return [response.text, status, "html"]
