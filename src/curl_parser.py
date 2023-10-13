from argparse import ArgumentParser
from shlex import split

class CurlParser():

    def __init__(self, curl):
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
        return dict([self.__split_header(header) for header in headers])

    def __split_header(self, header: str) -> tuple:
        header_split = header.split(': ')
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
        return self.__data.url
    
    @property
    def cookies(self) -> dict[str, str]:
        return self.__cookies
