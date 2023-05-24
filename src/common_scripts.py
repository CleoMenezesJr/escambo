# Copyright 2023 Cleo Menezes Jr.
# SPDX-License-Identifier: GPL-3.0-or-later

import re


def is_valid_url(url: str) -> bool:
    regex = re.compile(
        r"^(?:http|ftp)s?://"
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"
        r"localhost|"
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
        r"(?::\d+)?"
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    return re.match(regex, url)


def has_parameter(url: str) -> bool:
    return "?" in url


def stringfy_cookie(*args) -> str:
    """Return a formatted string from cookie dictionary"""
    cookie_key = args[0]
    cookie_value = args[1]

    name_and_value = f"{cookie_key}={cookie_value}; "
    expires = f"Expires={args[2]};"
    domain = f"Domain={args[3]};"
    path = f"Path={args[4]}"
    string_cookie = "{}{}{}{}".format(
        name_and_value,
        args[2] if not args[2] else f"{expires} ",
        args[3] if not args[3] else f"{domain} ",
        args[4] if not args[4] else path,
    )
    return string_cookie


def str_to_dict_cookie(cookies: str, id: str = None) -> dict:
    if id:
        splited_content = cookies[id][1].split(";")
    else:
        splited_content = cookies[1].split(";")

    dict_cookie = {}

    for i in splited_content:
        splited_values = i.split("=")
        if splited_content.index(i) == 0:
            dict_cookie["name"] = splited_values[0]
            dict_cookie["value"] = splited_values[1]
        else:
            if i.strip() != "":
                formatted_key = splited_values[0].strip().lower()
                formatted_value = splited_values[1].strip().lower()
                match formatted_key:
                    case "expires":
                        dict_cookie[formatted_key] = formatted_value
                    case "domain":
                        dict_cookie[formatted_key] = formatted_value
                    case "path":
                        dict_cookie[formatted_key] = formatted_value
    return dict_cookie

