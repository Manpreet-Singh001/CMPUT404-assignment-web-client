#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlparse, urlencode


class HTTPRequest:

    def __init__(self, url, method, headers=None, body=None):
        parsed_url = urlparse(url)
        self.host = parsed_url.hostname
        self.port = parsed_url.port if parsed_url.port is not None else 80
        self.query = parsed_url.query
        self.path = parsed_url.path if parsed_url.path != "" else "/"
        self.body = urlencode(body) if body is not None else {}
        self.method = method
        self.headers = headers if headers is not None else {}
        self.headers['Host'] = self.host
        self.headers['Accept'] = 'Accept: */*'
        self.headers['Connection'] = 'close'
        self.headers['Content-Length'] = len(self.body)


    def create_request(self):
        http_request = f'{self.method} {self.path}?{self.query} HTTP/1.1\r\n'
        for header in self.headers.keys():
            http_request += f'{header}: {self.headers[header]}\r\n'
        http_request += f'\r\n{self.body}'
        return http_request


class GETRequest(HTTPRequest):

    def __init__(self, url, body):
        super().__init__(url, 'GET')


class POSTRequest(HTTPRequest):

    def __init__(self, url, body):
        super().__init__(url, 'POST', body=body)
        self.headers['Content-Type'] = 'application/x-www-form-urlencoded'


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):
    # def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self):
        buffer = bytearray()
        done = False
        while not done:
            part = self.socket.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        self.close()
        return buffer.decode('utf-8')

    def send_request(self, request: HTTPRequest):

        self.connect(request.host, request.port)
        self.sendall(request.create_request())
        response = self.recvall()
        lines = response.split("\r\n")

        status = lines[0].split(" ")[1]
        body = response.split("\r\n\r\n")[-1]
        return HTTPResponse(int(status), body)

    def GET(self, url, args=None):
        args = args if args is not None else {}
        request = GETRequest(url, args)
        request.query = urlencode(args)
        response = self.send_request(request)
        return response

    def POST(self, url, args=None):
        response = self.send_request(POSTRequest(url, args))
        return response

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))
