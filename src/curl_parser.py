from argparse import ArgumentParser
from shlex import split
import re

class CurlParser():

    def __init__(self, curl: str):
        self.__curl = curl
        argv = split(curl.strip())
        del argv[0]
        try:
            self.__data = self.__get_parser().parse_args(argv)
        except:
            raise Exception('Invalid cURL format')
        else: 
            self.__headers = self.__create_headers_dict(self.__data.headers)
            self.__cookies = self.__create_cookies_dict(self.__data.cookies)
            self.__params = self.__create_params_dict(self.__data.url)

    def __get_parser(self) -> ArgumentParser:
        parser = ArgumentParser(add_help=False, exit_on_error=False)
        parser.add_argument('url')
        parser.add_argument('-X', '--request', dest='method', default='GET')
        parser.add_argument('-H', '--header', dest='headers', action='append')
        parser.add_argument('-b', '--cookie', dest='cookies', action='append')
        parser.add_argument('-d', '--data', dest='data', action='append')
        parser.add_argument('--data-raw', dest='data_raw', default=None)
        parser.add_argument('--data-binary', dest='data_binary', default=None)
        parser.add_argument('--compressed', action='store_true')
        parser.add_argument('-L', '--location', action='store_true')
        return parser

    def __create_headers_dict(self, headers: list[str]) -> dict[str, str]:
        if not headers: return dict()
        return dict([self.__split(header, ': ') for header in headers])

    def __split(self, header: str, divider: str) -> tuple:
        header_split = header.split(divider)
        return self.__build_tuple(header_split)
        
    def __build_tuple(self, list: list[str]) -> tuple[str, str]:
        return (list[0], list[1]) if len(list) > 1 else (list[0], "")
    
    def __create_cookies_dict(self, cookies: list[str]) -> dict[str, str]:
        if not cookies: return dict()
        result = dict[str, str]()
        for cookie in cookies:
            result = result | self.__split_cookie(cookie)
        return result

    def __split_cookie(self, cookie: str) -> dict[str, str]:
        cookie_entries = cookie.split('; ')
        result = dict[str, str]()
        currentEntry: str = ""
        currentEntryName: str = ""
        for entry in cookie_entries:
            entry_split = entry.split("=")
            entry_len = len(entry_split)
            match entry_split[0]:
                case 'Domain' | 'Path' | 'Expires' if currentEntry and entry_len > 1:
                    currentEntry = currentEntry + '; ' + entry
                    if entry_split[0] == 'Domain' and entry_split[1]: currentEntryName = entry_split[1]
                case 'Domain' | 'Path' | 'Expires': pass
                case _ if entry_len > 0:
                    if currentEntry: result[currentEntryName] = currentEntry
                    currentEntryName = entry_split[0]
                    if entry_len > 1: currentEntry = entry
                    else: currentEntry = entry_split[0] + "=" + entry_split[0]
        if currentEntry: result[currentEntryName] = currentEntry
        return result
    
    def __create_params_dict(self, url: str) -> dict[str, str]:
        q_match = re.search(r'\?((.+=[^#].+)#|(.+=.+)$)', url)
        if not q_match: return dict() 
        q_params = q_match.group(1).replace('#', "").split('&')
        return dict([self.__split(param, '=') for param in q_params])

    @property
    def headers(self) -> dict[str, str]:
        return {k:self.__headers[k] for k in self.__headers.keys() if not k == "Authorization"}

    @property
    def authorization(self) -> str:
        try: authHeader: str = self.__headers["Authorization"]
        except KeyError as e: return None
        else:
            if authHeader.startswith("Bearer"): return authHeader.split("Bearer ")[1]
            else: return authHeader

    @property
    def method(self) -> str:
        return self.__data.method

    @property
    def url(self) -> str:
        return self.__data.url.split('?')[0]
    
    @property
    def cookies(self) -> dict[str, str]:
        return self.__cookies
    
    @property
    def params(self) -> dict[str, str]:
        return self.__params
    
    @property 
    def body(self) -> str | dict[str, str] | None:
        if self.__data.data_raw: return self._data.data_raw
        elif self.__data.data: return self.__data.data
        else: return None 
    
# parsed = CurlParser("curl http://a.b.c/aaa?b=b&d=d&e=e&f=F#title")
# print(parsed.params)
