import datetime
import json
import time

import requests
from escambo.commom_scripts import str_to_dict_cookie


class ResolveRequests:
    def __init__(
        self,
        url: str,
        session: requests.sessions.Session,
        cookies: dict = None,
        headers: dict = None,
        body: dict = None,
        parameters: dict = None,
        authentication: dict = None,
    ) -> None:
        # common variables and references
        self.url = url
        self.session = session
        self.body = body
        self.params = parameters
        self.cookies = cookies
        self.auths = authentication

        if self.cookies:
            self.set_cookie_session()
        if headers:
            self.session.headers.update(headers)
        if self.auths:
            self.set_auth()
        if not self.body:
            self.body = {}

    def resolve_get(self) -> list:
        response = self.session.get(
            self.url,
            json=self.body,
            params=self.params,
        )
        return self.formated_response(response)

    def resolve_post(self) -> list:
        response = self.session.post(
            self.url,
            json=self.body,
            params=self.params,
        )

        return self.formated_response(response)

    def resolve_put(self) -> list:
        response = self.session.put(
            self.url,
            json=self.body,
            params=self.params,
        )

        return self.formated_response(response)

    def resolve_patch(self) -> list:
        response = self.session.patch(
            self.url,
            json=self.body,
            params=self.params,
        )

        return self.formated_response(response)

    def resolve_delete(self) -> list:
        response = self.session.patch(
            self.url,
            json=self.body,
            params=self.params,
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

    def set_cookie_session(self) -> None:
        for id, cookie in self.cookies.items():
            cookie_dict = {}
            cookie_content = str_to_dict_cookie(cookie)

            cookie_dict["name"] = cookie_content["name"]
            cookie_dict["value"] = cookie_content["value"]
            if "domain" in cookie_content.keys():
                cookie_dict["domain"] = cookie_content["domain"]
            if "path" in cookie_content.keys():
                cookie_dict["path"] = cookie_content["path"]
            if "expires" in cookie_content.keys():
                expires_str = cookie_content["expires"]
                expires_datetime = datetime.datetime.strptime(
                    expires_str, "%a, %d %b %Y %H:%M:%S %Z"
                )
                expires_unix = int(time.mktime(expires_datetime.timetuple()))
                cookie_dict["expires"] = expires_unix

            self.session.cookies.set(**cookie_dict)

    def set_auth(self) -> None:
        auth_type = self.auths[0].props.selected_item.get_string()
        auth_values = self.auths[1]
        match auth_type:
            case "Api Key":
                if (
                    not auth_values[auth_type][0]
                    and not auth_values[auth_type][1]
                ):
                    return

                if auth_values[auth_type][2] == "Query Parameters":
                    self.params |= {
                        auth_values[auth_type][0]: auth_values[auth_type][1]
                    }
                elif auth_values[auth_type][2] == "Header":
                    self.session.headers.update(
                        {auth_values[auth_type][0]: auth_values[auth_type][1]}
                    )
            case "Bearer Token":
                if not auth_values[auth_type][0]:
                    return
                self.session.headers.update(
                    {"Authorization": f"Bearer {auth_values[auth_type][0]}"}
                )
