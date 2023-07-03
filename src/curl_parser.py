import argparse
import json
import shlex

curl_command5 = """curl -X POST -H 'Authorization: Bearer token' -d "{'resourceNetworkInterface':[{'ipAddress': 'ipaddress'}]}" 'https://$$opsramp_instance.com/api/v2/tenants/$$tenantId/resources/$resourceId'"""

# print(argv)

class CurlParser():

    def __init__(self, curl):
        
        self.__curl = curl
        argv = shlex.split(curl.strip())
        del argv[0]

        parser = argparse.ArgumentParser()
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
        self.__data = parser.parse_args(argv)
        if self.__data.headers:
            self.__headers = dict([self.__split_header(header) for header in self.__data.headers])
        else:
            self.__headers = dict()
        # print(self.__data)

    def __split_header(sefl, header):
        header_split = header.split(': ')
        return (header_split[0], header_split[1])

    @property
    def headers(self):
        return {k:self.__headers[k] for k in self.__headers.keys() if not k == "Authorization"}

    @property
    def authorization(self):
        try:
            authHeader = self.__headers["Authorization"]
        except KeyError as e:
            print("no Authorization header")
            return None
        else:
            return authHeader

    @property
    def method(self):
        return self.__data.method

    @property
    def url(self):
        return self.__data.url
