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
            print('Catching an argumentError')
        else: 
            self.__headers = self.__create_headers_dict(self.__data.headers)
            # print(self.__data)

    def __get_parser(self) -> ArgumentParser:
        parser = ArgumentParser(add_help=False, exit_on_error=False)
        parser.add_argument('url')
        parser.add_argument('-d', '--data')
        parser.add_argument('-b', '--data-binary', '--data-raw', default=None)
        parser.add_argument('--request', '-X', dest='method', default='GET')
        parser.add_argument('--header', '-H', dest='headers', action='append')
        parser.add_argument('--compressed', action='store_true')
        parser.add_argument('-k', '--insecure', action='store_true')
        parser.add_argument('--user', '-u', default=())
        parser.add_argument('-i', '--include', action='store_true')
        parser.add_argument('-s', '--silent', action='store_true')
        return parser

    def __create_headers_dict(self, headers) -> dict:
        if not self.__data.headers: return dict()
        return dict([self.__split_header(header) for header in headers])

    def __split_header(sefl, header):
        header_split = header.split(': ')
        return (header_split[0], header_split[1])

    @property
    def headers(self) -> dict[str, str]:
        return {k:self.__headers[k] for k in self.__headers.keys() if not k == "Authorization"}

    @property
    def authorization(self) -> str:
        try:
            authHeader = self.__headers["Authorization"]
        except KeyError as e:
            print("no Authorization header")
            return None
        else:
            return authHeader

    @property
    def method(self) -> str:
        return self.__data.method

    @property
    def url(self) -> str:
        return self.__data.url
